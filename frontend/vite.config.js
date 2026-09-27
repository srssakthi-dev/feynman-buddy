import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  cacheDir: "../.local/vite",
  resolve: { preserveSymlinks: true },
  server: {
    host: '127.0.0.1',
    port: 5174,
    strictPort: true,
    proxy: { '/api': process.env.FEYNMAN_API_TARGET || 'http://127.0.0.1:8001' },
  },
})
