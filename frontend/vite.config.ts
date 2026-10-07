import { defineConfig } from "vite";

export default defineConfig({
  server: {
    port: 3000,
    host: "127.0.0.1",
    proxy: {
      "/health": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        ws: true,
      },
    },
  },
});
