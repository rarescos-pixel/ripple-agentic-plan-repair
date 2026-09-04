import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const targetUrl = process.env.TARGET_URL || 'https://example.com';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/browser-poc';
const screenshotPath = path.join(artifactDir, 'page.png');
const resultPath = path.join(artifactDir, 'result.json');

await fs.mkdir(artifactDir, { recursive: true });

let browser;
const startedAt = new Date().toISOString();

try {
  const parsed = new URL(targetUrl);
  if (!['http:', 'https:'].includes(parsed.protocol)) {
    throw new Error(`Unsupported protocol: ${parsed.protocol}`);
  }

  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
  });
  const page = await context.newPage();

  const response = await page.goto(targetUrl, {
    waitUntil: 'domcontentloaded',
    timeout: 30_000,
  });

  const title = await page.title();
  const finalUrl = page.url();
  const status = response?.status() ?? null;

  await page.screenshot({ path: screenshotPath, fullPage: true });

  const result = {
    ok: true,
    targetUrl,
    finalUrl,
    title,
    httpStatus: status,
    screenshot: screenshotPath,
    startedAt,
    finishedAt: new Date().toISOString(),
  };

  await fs.writeFile(resultPath, JSON.stringify(result, null, 2) + '\n', 'utf8');
  console.log(JSON.stringify(result));
} catch (error) {
  const result = {
    ok: false,
    targetUrl,
    error: error instanceof Error ? error.message : String(error),
    startedAt,
    finishedAt: new Date().toISOString(),
  };
  await fs.writeFile(resultPath, JSON.stringify(result, null, 2) + '\n', 'utf8');
  console.error(JSON.stringify(result));
  process.exitCode = 1;
} finally {
  await browser?.close();
}
