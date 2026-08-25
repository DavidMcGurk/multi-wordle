import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Set VITE_BASE_PATH=/multi-wordle/ for GitHub Pages project sites.
  // Defaults to '/' for local dev and custom domains.
  base: process.env.VITE_BASE_PATH || '/',
})
