import { defineConfig, devices } from '@playwright/test';

/**
 * Trusted Types is enforced only by Chromium, so the E2E runs there alone.
 * The production build is served statically and the enforcing CSP is injected
 * per-request in the spec (Cloudflare applies it in prod via `public/_headers`).
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? 'list' : 'html',
  use: {
    baseURL: 'http://localhost:4321',
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: 'npx http-server dist/frontend/browser -p 4321 -c-1 --silent',
    url: 'http://localhost:4321',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
