import { copyFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

const copies = [
  {
    from: join(root, "aave-v3-loop-analysis", "data.json"),
    to: join(root, "dist", "aave-v3-loop-analysis", "data.json"),
  },
];

for (const { from, to } of copies) {
  if (!existsSync(from)) {
    console.warn(`skip missing asset: ${from}`);
    continue;
  }
  mkdirSync(dirname(to), { recursive: true });
  copyFileSync(from, to);
  console.log(`copied ${from} -> ${to}`);
}
