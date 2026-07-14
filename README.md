# Public static site

Mirror of `app/` for Netlify (or Vercel). Showcase HTML only — no local research paths, PDFs, or pipeline CSVs with `source_file` columns.

## Pages

- `/` — overview
- `/us-treasuries/` — U.S. Treasury holdings dashboard
- `/m2-stablecoins/` — U.S. M2 vs stablecoin supply

## Deploy (Netlify)

1. Connect this GitHub repo in [Netlify](https://app.netlify.com) → **Add new site** → **Import an existing project**.
2. Build settings: **no build command**; publish directory = `/` (repo root). `netlify.toml` already sets this.
3. After deploy, add custom domain (e.g. `macrorwa.xyz`) under **Domain management**.
4. Point DNS at Netlify (easiest: use Netlify DNS, or add the A/CNAME records Netlify shows).

## Sources (shown in-page)

- TIC Major Foreign Holders
- Issuer attestation reports
- RWA.xyz
- FRED M2SL / Federal Reserve H.6 / Fed funds
