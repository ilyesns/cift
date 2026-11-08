import { fileURLToPath, URL } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  server: {
    host: true,
    port: 5174,
    strictPort: true, // fail loudly instead of silently moving to another port (CORS would break)
    // File events don't always cross the Docker bind mount; polling fixes hot reload if needed
    watch: { usePolling: process.env.VITE_POLLING === "true" },
  },
  test: {
    environment: "jsdom",
  },
});