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
      },
    },
    {
      command: 'npm run preview -- --port 4173 --strictPort',
      port: 4173,
      reuseExistingServer: false,
      env: {
        VITE_API_URL: '',
      },
    },
  ],
});
