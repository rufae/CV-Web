import { fileURLToPath, URL } from 'node:url';

import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Destino del backend en desarrollo. Por defecto, el backend local del
  // runbook (uvicorn en 127.0.0.1:8000). Para desarrollar contra el
  // desplegado: VITE_DEV_API_TARGET=http://<nodo>:8086 npm run dev
  // (bug 2026-10-01: apuntaba a 127.0.0.1:8010, el puerto de Rafita, y el
  // chat del CVWEB no respondia).
  const env = loadEnv(mode, process.cwd(), '');
  const apiTarget = env.VITE_DEV_API_TARGET || 'http://127.0.0.1:8000';

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api': { target: apiTarget, changeOrigin: true },
      },
    },
    preview: {
      proxy: {
        '/api': { target: apiTarget, changeOrigin: true },
      },
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    test: {
      setupFiles: ['./src/test/setup.ts'],
      exclude: ['e2e/**', 'node_modules/**', 'dist/**', 'dist-ssr/**'],
    },
  };
});
