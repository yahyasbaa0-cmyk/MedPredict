import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 9654,
    strictPort: true,
    watch: {
      usePolling: true,
    },
    hmr: {
      clientPort: 9654,
    },
  },
})
