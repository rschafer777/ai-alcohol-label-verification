import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 45_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  forbidOnly: true,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: process.env.LABELVERIFY_E2E_URL ?? "http://127.0.0.1:8000",
    headless: true,
    trace: "retain-on-failure",
  },
  webServer: {
    command: "uv run uvicorn labelverify.api.app:app --app-dir backend --host 127.0.0.1 --port 8000 --no-access-log",
    cwd: "..",
    reuseExistingServer: true,
    timeout: 30_000,
    url: "http://127.0.0.1:8000/health/ready",
  },
  projects: [
    { name: "chrome", use: { ...devices["Desktop Chrome"], channel: "chrome" } },
    { name: "edge", use: { ...devices["Desktop Edge"], channel: "msedge" } },
  ],
});
