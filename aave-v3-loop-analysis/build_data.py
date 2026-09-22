"""Rebuild dashboard/data.json from pipeline CSVs."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent / "data.json"

STAKED = {
    "wstETH",
    "weETH",
    "ezETH",
    "rETH",
    "cbETH",
    "osETH",
    "ETHx",
    "rsETH",
    "tETH",
    "stETH",
}
RECYCLABLE = {
    "WETH",
    "USDC",
    "USDT",
    "DAI",
    "GHO",
    "USDe",
    "USDS",
    "EURC",
    "PYUSD",
    "USDtb",
    "crvUSD",
    "FRAX",
    "wstETH",
}
ETH_LIKE_BORROW = {"WETH", "wstETH"}
USD_BORROW = RECYCLABLE - ETH_LIKE_BORROW


def main() -> None:
    deps = list(csv.DictReader((DATA / "deposits.csv").open(encoding="utf-8")))
    bors = list(csv.DictReader((DATA / "borrows.csv").open(encoding="utf-8")))
    summ = list(
        csv.DictReader((DATA / "user_summary_by_staked_eth.csv").open(encoding="utf-8"))
    )

    by_user: dict[str, dict] = {}
    for r in summ:
        u = r["user"].lower()
        by_user[u] = {
            "user": u,
            "total_deposits_usd": float(r["total_supply_usd"]),
            "total_borrow_usd": float(r["total_borrow_usd"]),
            "staked_eth_deposits_usd": float(r["staked_eth_supply_usd"]),
            "net_usd": float(r["net_supply_minus_borrow_usd"]),
            "supply_positions": int(r["supply_positions"]),
            "borrow_positions": int(r["borrow_positions"]),
            "health_factors": r.get("health_factors", ""),
            "recyclable_borrow_usd": 0.0,
            "eth_like_borrow_usd": 0.0,
            "usd_stable_borrow_usd": 0.0,
            "other_borrow_usd": 0.0,
            "non_staked_deposits_usd": 0.0,
            "borrow_by_symbol": defaultdict(float),
            "deposit_by_symbol": defaultdict(float),
        }

    for r in deps:
        u = r["user"].lower()
        if u not in by_user:
            continue
        usd = float(r["usd"])
        sym = r["symbol"]
        by_user[u]["deposit_by_symbol"][sym] += usd
        if sym not in STAKED:
            by_user[u]["non_staked_deposits_usd"] += usd

    for r in bors:
        u = r["user"].lower()
        if u not in by_user:
            continue
        usd = float(r["usd"])
        sym = r["symbol"]
        by_user[u]["borrow_by_symbol"][sym] += usd
        if sym in ETH_LIKE_BORROW:
            by_user[u]["eth_like_borrow_usd"] += usd
            by_user[u]["recyclable_borrow_usd"] += usd
        elif sym in USD_BORROW:
            by_user[u]["usd_stable_borrow_usd"] += usd
            by_user[u]["recyclable_borrow_usd"] += usd
        else:
            by_user[u]["other_borrow_usd"] += usd

    users = []
    for d in by_user.values():
        staked = d["staked_eth_deposits_usd"]
        rec = d["recyclable_borrow_usd"]
        tot_b = d["total_borrow_usd"]
        tot_d = d["total_deposits_usd"]
        d["loop_borrow_vs_staked"] = (rec / staked) if staked > 0 else 0.0
        d["ltv_total"] = (tot_b / tot_d) if tot_d > 0 else 0.0
        d["recyclable_share_of_borrow"] = (rec / tot_b) if tot_b > 0 else 0.0
        d["staked_share_of_deposits"] = (staked / tot_d) if tot_d > 0 else 0.0
        d["borrow_by_symbol"] = dict(d["borrow_by_symbol"])
        d["deposit_by_symbol"] = dict(d["deposit_by_symbol"])
        users.append(d)

    users.sort(key=lambda x: x["staked_eth_deposits_usd"], reverse=True)

    agg = {
        "n_users": len(users),
        "total_deposits_usd": sum(u["total_deposits_usd"] for u in users),
        "total_borrow_usd": sum(u["total_borrow_usd"] for u in users),
        "staked_eth_deposits_usd": sum(u["staked_eth_deposits_usd"] for u in users),
        "recyclable_borrow_usd": sum(u["recyclable_borrow_usd"] for u in users),
        "eth_like_borrow_usd": sum(u["eth_like_borrow_usd"] for u in users),
        "usd_stable_borrow_usd": sum(u["usd_stable_borrow_usd"] for u in users),
        "other_borrow_usd": sum(u["other_borrow_usd"] for u in users),
        "non_staked_deposits_usd": sum(u["non_staked_deposits_usd"] for u in users),
    }
    agg["loop_borrow_vs_staked"] = (
        agg["recyclable_borrow_usd"] / agg["staked_eth_deposits_usd"]
        if agg["staked_eth_deposits_usd"]
        else 0.0
    )
    agg["ltv_total"] = (
        agg["total_borrow_usd"] / agg["total_deposits_usd"]
        if agg["total_deposits_usd"]
        else 0.0
    )
    agg["recyclable_share_of_borrow"] = (
        agg["recyclable_borrow_usd"] / agg["total_borrow_usd"]
        if agg["total_borrow_usd"]
        else 0.0
    )

    borrow_comp: dict[str, float] = defaultdict(float)
    for u in users:
        for s, v in u["borrow_by_symbol"].items():
            borrow_comp[s] += v
    borrow_comp_sorted = sorted(borrow_comp.items(), key=lambda x: -x[1])

    buckets = {"0": 0, "0-25%": 0, "25-50%": 0, "50-75%": 0, "75-100%": 0, "100%+": 0}
    for u in users:
        ratio = u["loop_borrow_vs_staked"]
        if u["total_borrow_usd"] <= 1:
            buckets["0"] += 1
        elif ratio < 0.25:
            buckets["0-25%"] += 1
        elif ratio < 0.5:
            buckets["25-50%"] += 1
        elif ratio < 0.75:
            buckets["50-75%"] += 1
        elif ratio < 1.0:
            buckets["75-100%"] += 1
        else:
            buckets["100%+"] += 1

    top20 = [
        {
            "user": u["user"],
            "short": u["user"][:6] + "…" + u["user"][-4:],
            "staked_eth_deposits_usd": u["staked_eth_deposits_usd"],
            "recyclable_borrow_usd": u["recyclable_borrow_usd"],
            "total_borrow_usd": u["total_borrow_usd"],
            "total_deposits_usd": u["total_deposits_usd"],
            "loop_borrow_vs_staked": u["loop_borrow_vs_staked"],
        }
        for u in users[:20]
    ]

    out = {
        "meta": {
            "title": "Aave V3 Ethereum — Staked ETH Loop Dashboard",
            "cohort": "Top 200 unique holders by staked-ETH aToken USD",
            "staked_symbols": sorted(STAKED),
            "recyclable_symbols": sorted(RECYCLABLE),
            "definition": (
                "Recyclable borrow = WETH + USD stables (and wstETH) that can be "
                "swapped into ETH/LSTs and re-deposited — the loop amplifier."
            ),
        },
        "aggregate": agg,
        "borrow_composition": borrow_comp_sorted,
        "loop_ratio_buckets": buckets,
        "top20": top20,
        "users": users,
    }
    OUT.write_text(json.dumps(out), encoding="utf-8")
    print(f"Wrote {OUT} ({len(users)} users)")


if __name__ == "__main__":
    main()
