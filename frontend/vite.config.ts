import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  optimizeDeps: {
    include: ['firebase/auth', 'firebase/app', 'firebase/firestore', 'firebase/storage']
  },
  server: {
    port: 3000,
    host: true,
    strictPort: true,
    hmr: {
      port: 3000
    }
  }
})