import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

const __dirname = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, "index.html"),
        treasuries: resolve(__dirname, "us-treasuries/index.html"),
        m2: resolve(__dirname, "m2-stablecoins/index.html"),
      },
    },
  },
});
