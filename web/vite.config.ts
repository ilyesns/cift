import { fileURLToPath, URL } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  server: {
    host: true,
    port: 5174,
    strictPort: true,
    watch: { usePolling: process.env.VITE_POLLING === "true" },
    proxy: {
      "/api": { target: "http://localhost:8010", changeOrigin: true },
    },
  },
  
});