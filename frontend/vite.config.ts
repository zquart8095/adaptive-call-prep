import path from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    // Pinned so langgraph.json's CORS allow_origins stays correct — Vite
    // auto-increments this if busy, which would silently break CORS.
    port: 5173,
    strictPort: true,
  },
})
