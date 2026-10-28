import { defineConfig } from "@playwright/test";


export default defineConfig({
  testDir: "./frontend/tests/integration",
  fullyParallel: false,
  workers: 1,
  timeout: 60_000,
  reporter: "line",
  use: {
    baseURL: process.env.MSEN_BASE_URL ?? "http://127.0.0.1:5051",
    browserName: "chromium",
    channel: "chrome",
    headless: true,
    viewport: { width: 1280, height: 900 },
  },
});
