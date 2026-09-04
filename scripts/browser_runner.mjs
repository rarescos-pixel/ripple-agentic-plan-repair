import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const requestPath = process.env.BROWSER_REQUEST_PATH || 'automation/browser-request.json';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/browser-runner';
const resultPath = path.join(artifactDir, 'result.json');
const maxSteps = 30;

await fs.mkdir(artifactDir, { recursive: true });

const startedAt = new Date().toISOString();
let browser;
let result = {
  ok: false,
  requestPath,
  startedAt,
  steps: [],
};

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function safeArtifactName(name, fallback = 'screenshot.png') {
  const candidate = String(name || fallback).replace(/[^A-Za-z0-9._-]/g, '_');
  return candidate.endsWith('.png') ? candidate : `${candidate}.png`;
}

function resolveSecretValue(step) {
  if (step.valueFromEnv) {
    const envName = String(step.valueFromEnv);
    const value = process.env[envName];
    assert(value !== undefined, `Required environment variable is missing: ${envName}`);
    return value;
  }
  return step.value ?? '';
}

function timeoutFor(step, request) {
  const raw = Number(step.timeoutMs ?? request.timeoutMs ?? 30_000);
  return Number.isFinite(raw) ? Math.max(1, Math.min(raw, 120_000)) : 30_000;
}

try {
  const raw = await fs.readFile(requestPath, 'utf8');
  const request = JSON.parse(raw);

  assert(request && typeof request === 'object', 'Request must be a JSON object');
  assert(typeof request.url === 'string' && request.url.length > 0, 'Request.url is required');

  const parsedUrl = new URL(request.url);
  assert(['http:', 'https:'].includes(parsedUrl.protocol), `Unsupported protocol: ${parsedUrl.protocol}`);

  const steps = Array.isArray(request.steps) ? request.steps : [];
  assert(steps.length <= maxSteps, `Too many steps: ${steps.length}; maximum is ${maxSteps}`);

  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    acceptDownloads: true,
  });
  const page = await context.newPage();

  const navigationResponse = await page.goto(request.url, {
    waitUntil: request.waitUntil || 'domcontentloaded',
    timeout: timeoutFor({}, request),
  });

  result = {
    ...result,
    targetUrl: request.url,
    initialHttpStatus: navigationResponse?.status() ?? null,
  };

  for (let index = 0; index < steps.length; index += 1) {
    const step = steps[index];
    assert(step && typeof step === 'object', `Step ${index + 1} must be an object`);
    const action = String(step.action || '');
    assert(action, `Step ${index + 1} is missing action`);

    const stepResult = { index: index + 1, action, ok: false };
    try {
      switch (action) {
        case 'click':
          assert(step.selector, `Step ${index + 1}: selector is required`);
          await page.locator(step.selector).click({ timeout: timeoutFor(step, request) });
          break;

        case 'fill':
          assert(step.selector, `Step ${index + 1}: selector is required`);
          await page.locator(step.selector).fill(String(resolveSecretValue(step)), {
            timeout: timeoutFor(step, request),
          });
          break;

        case 'press':
          assert(step.selector && step.key, `Step ${index + 1}: selector and key are required`);
          await page.locator(step.selector).press(String(step.key), { timeout: timeoutFor(step, request) });
          break;

        case 'check':
          assert(step.selector, `Step ${index + 1}: selector is required`);
          await page.locator(step.selector).check({ timeout: timeoutFor(step, request) });
          break;

        case 'selectOption':
          assert(step.selector, `Step ${index + 1}: selector is required`);
          await page.locator(step.selector).selectOption(step.value, { timeout: timeoutFor(step, request) });
          break;

        case 'setInputFiles': {
          assert(step.selector, `Step ${index + 1}: selector is required`);
          const files = Array.isArray(step.files) ? step.files : [step.file].filter(Boolean);
          assert(files.length > 0, `Step ${index + 1}: file or files is required`);
          const resolvedFiles = files.map((file) => path.resolve(String(file)));
          for (const file of resolvedFiles) await fs.access(file);
          await page.locator(step.selector).setInputFiles(resolvedFiles, { timeout: timeoutFor(step, request) });
          break;
        }

        case 'waitForSelector':
          assert(step.selector, `Step ${index + 1}: selector is required`);
          await page.locator(step.selector).waitFor({
            state: step.state || 'visible',
            timeout: timeoutFor(step, request),
          });
          break;

        case 'waitForTimeout': {
          const ms = Math.max(0, Math.min(Number(step.ms || 0), 10_000));
          await page.waitForTimeout(ms);
          break;
        }

        case 'assertText': {
          assert(step.selector, `Step ${index + 1}: selector is required`);
          const text = (await page.locator(step.selector).textContent({ timeout: timeoutFor(step, request) })) ?? '';
          if (step.equals !== undefined) assert(text.trim() === String(step.equals), `Text assertion failed at ${step.selector}`);
          if (step.contains !== undefined) assert(text.includes(String(step.contains)), `Text assertion failed at ${step.selector}`);
          stepResult.observedText = text.trim().slice(0, 500);
          break;
        }

        case 'assertTitle': {
          const title = await page.title();
          if (step.equals !== undefined) assert(title === String(step.equals), 'Title assertion failed');
          if (step.contains !== undefined) assert(title.includes(String(step.contains)), 'Title assertion failed');
          stepResult.observedTitle = title;
          break;
        }

        case 'assertUrl': {
          const currentUrl = page.url();
          if (step.equals !== undefined) assert(currentUrl === String(step.equals), 'URL assertion failed');
          if (step.contains !== undefined) assert(currentUrl.includes(String(step.contains)), 'URL assertion failed');
          stepResult.observedUrl = currentUrl;
          break;
        }

        case 'screenshot': {
          const name = safeArtifactName(step.name, `step-${index + 1}.png`);
          const screenshotPath = path.join(artifactDir, name);
          await page.screenshot({ path: screenshotPath, fullPage: step.fullPage !== false });
          stepResult.artifact = screenshotPath;
          break;
        }

        default:
          throw new Error(`Unsupported action at step ${index + 1}: ${action}`);
      }

      stepResult.ok = true;
      result.steps.push(stepResult);
    } catch (error) {
      stepResult.error = error instanceof Error ? error.message : String(error);
      result.steps.push(stepResult);
      throw error;
    }
  }

  const finalScreenshot = path.join(artifactDir, safeArtifactName(request.finalScreenshot, 'final.png'));
  await page.screenshot({ path: finalScreenshot, fullPage: true });

  result = {
    ...result,
    ok: true,
    finalUrl: page.url(),
    title: await page.title(),
    finalScreenshot,
    finishedAt: new Date().toISOString(),
  };
} catch (error) {
  result = {
    ...result,
    ok: false,
    error: error instanceof Error ? error.message : String(error),
    finishedAt: new Date().toISOString(),
  };
  process.exitCode = 1;
} finally {
  await browser?.close();
  await fs.writeFile(resultPath, JSON.stringify(result, null, 2) + '\n', 'utf8');
  console.log(JSON.stringify(result));
}
