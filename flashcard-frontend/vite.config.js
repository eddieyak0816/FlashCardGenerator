import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';


export default defineConfig({
  plugins: [react()],
  css: {
    postcss: './postcss.config.js',
  },
  server: {
    proxy: {
      '/generate': 'http://localhost:5000',
      '/export': 'http://localhost:5000',
    },
  },
});
