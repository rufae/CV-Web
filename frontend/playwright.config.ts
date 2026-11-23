import { defineConfig, devices } from '@playwright/test';

const PYTHON = process.env.PYTHON_BIN ?? 'python3';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  fullyParallel: true,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    baseURL: 'http://127.0.0.1:4173',
    locale: 'es-ES',
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    {
      command: `${PYTHON} -m uvicorn app.main:app --app-dir ../backend --host 127.0.0.1 --port 8010`,
      port: 8010,
      reuseExistingServer: false,
      env: {
        APP_ENV: 'test',
        DATA_PATH: '/tmp/cvweb-e2e-data',
        RATE_LIMIT_CHAT: '100/minute',
        RATE_LIMIT_CONTACT: '100/hour',
        // El preview sirve en :4173; el backend debe permitir ese origen
        // (por defecto sólo admite :5173, el dev server).
        ALLOWED_ORIGINS: 'http://localhost:4173,http://127.0.0.1:4173,http://localhost:5173,http://127.0.0.1:5173',
      },
    },
    {
      // vite preview sirve dist (lo construye el paso `npm run build` del
      // job); la app apunta al backend en absoluto (sin proxy de preview).
      command: 'npm run preview -- --port 4173 --strictPort',
      port: 4173,
      timeout: 60_000,
      // En CI el preview lo levanta el propio job (con health check) y aquí
      // sólo se reutiliza; en local lo arranca Playwright.
      reuseExistingServer: true,
      env: {
        VITE_API_URL: 'http://127.0.0.1:8010',
      },
    },
  ],
});
