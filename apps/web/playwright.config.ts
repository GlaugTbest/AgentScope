import { chromium, defineConfig } from '@playwright/test';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';

const repositoryRoot = resolve(__dirname, '../..');
const bundledBrowser = chromium.executablePath();
const localChromium = process.platform === 'win32'
  ? 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
  : undefined;
const executablePath = existsSync(bundledBrowser)
  ? bundledBrowser
  : localChromium && existsSync(localChromium)
    ? localChromium
    : undefined;

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:3100',
    trace: 'on-first-retry',
    launchOptions: executablePath ? { executablePath } : {},
  },
  webServer: {
    command: `"${process.execPath}" scripts/e2e-server.mjs`,
    cwd: repositoryRoot,
    url: 'http://127.0.0.1:3100',
    timeout: 120_000,
    reuseExistingServer: false,
  },
});
