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
let context;
let page;
let providerState = { provider: 'local' };
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

function nonEmpty(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

async function browserbaseRequest(apiKey, pathname, options = {}) {
  const response = await fetch(`https://api.browserbase.com${pathname}`, {
    ...options,
    headers: {
      'content-type': 'application/json',
      'x-bb-api-key': apiKey,
      ...(options.headers || {}),
    },
  });

  const text = await response.text();
  let body = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = { raw: text.slice(0, 500) };
    }
  }

  if (!response.ok) {
    throw new Error(`Browserbase API ${response.status} at ${pathname}`);
  }
  return body;
}

async function openBrowser(request) {
  const provider = String(request.provider || 'local').toLowerCase();

  if (provider === 'local') {
    const localBrowser = await chromium.launch({ headless: true });
    const localContext = await localBrowser.newContext({
      viewport: { width: 1440, height: 1000 },
      acceptDownloads: true,
    });
    const localPage = await localContext.newPage();
    return {
      browser: localBrowser,
      context: localContext,
      page: localPage,
      providerState: { provider: 'local' },
    };
  }

  if (provider !== 'browserbase') {
    throw new Error(`Unsupported browser provider: ${provider}`);
  }

  const apiKeyEnv = request.browserbase?.apiKeyFromEnv || 'BROWSERBASE_API_KEY';
  const apiKey = process.env[apiKeyEnv];
  assert(nonEmpty(apiKey), `Browserbase API key is missing from environment variable ${apiKeyEnv}`);

  let projectId = request.browserbase?.projectId || process.env.BROWSERBASE_PROJECT_ID || '';
  let contextId = request.browserbase?.contextId || process.env.BROWSERBASE_CONTEXT_ID || '';

  if (!contextId && request.browserbase?.createContext === true) {
    const body = {};
    if (projectId) body.projectId = projectId;
    const createdContext = await browserbaseRequest(apiKey, '/v1/contexts', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    contextId = createdContext?.id || '';
    assert(nonEmpty(contextId), 'Browserbase did not return a context id');
  }

  assert(nonEmpty(contextId), 'Browserbase contextId is required for persistent authenticated mode');

  const sessionBody = {
    browserSettings: {
      context: {
        id: contextId,
        persist: request.browserbase?.persist !== false,
      },
      viewport: { width: 1440, height: 1000 },
    },
  };
  if (projectId) sessionBody.projectId = projectId;

  const session = await browserbaseRequest(apiKey, '/v1/sessions', {
    method: 'POST',
    body: JSON.stringify(sessionBody),
  });

  assert(nonEmpty(session?.connectUrl), 'Browserbase did not return a connectUrl');
  const remoteBrowser = await chromium.connectOverCDP(session.connectUrl);
  const contexts = remoteBrowser.contexts();
  assert(contexts.length > 0, 'Browserbase session has no browser context');
  const remoteContext = contexts[0];
  let remotePage = remoteContext.pages()[0];
  if (!remotePage) remotePage = await remoteContext.newPage();

  return {
    browser: remoteBrowser,
    context: remoteContext,
    page: remotePage,
    providerState: {
      provider: 'browserbase',
      sessionId: session.id || null,
      contextId,
      contextPersist: request.browserbase?.persist !== false,
    },
  };
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

  const sensitive = request.sensitive === true;
  const allowArtifacts = request.allowArtifacts === true && !sensitive;

  ({ browser, context, page, providerState } = await openBrowser(request));

  const navigationResponse = await page.goto(request.url, {
    waitUntil: request.waitUntil || 'domcontentloaded',
    timeout: timeoutFor({}, request),
  });

  result = {
    ...result,
    ...providerState,
    sensitive,
    artifactsAllowed: allowArtifacts,
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
          if (!sensitive) stepResult.observedText = text.trim().slice(0, 500);
          break;
        }

        case 'assertTitle': {
          const title = await page.title();
          if (step.equals !== undefined) assert(title === String(step.equals), 'Title assertion failed');
          if (step.contains !== undefined) assert(title.includes(String(step.contains)), 'Title assertion failed');
          if (!sensitive) stepResult.observedTitle = title;
          break;
        }

        case 'assertUrl': {
          const currentUrl = page.url();
          if (step.equals !== undefined) assert(currentUrl === String(step.equals), 'URL assertion failed');
          if (step.contains !== undefined) assert(currentUrl.includes(String(step.contains)), 'URL assertion failed');
          if (!sensitive) stepResult.observedUrl = currentUrl;
          break;
        }

        case 'screenshot': {
          assert(allowArtifacts, `Step ${index + 1}: screenshots are disabled unless allowArtifacts=true and sensitive=false`);
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

  let finalScreenshot = null;
  if (allowArtifacts) {
    finalScreenshot = path.join(artifactDir, safeArtifactName(request.finalScreenshot, 'final.png'));
    await page.screenshot({ path: finalScreenshot, fullPage: true });
  }

  result = {
    ...result,
    ok: true,
    ...(sensitive ? {} : { finalUrl: page.url(), title: await page.title() }),
    ...(finalScreenshot ? { finalScreenshot } : {}),
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
  try {
    await browser?.close();
  } finally {
    await fs.writeFile(resultPath, JSON.stringify(result, null, 2) + '\n', 'utf8');
    console.log(JSON.stringify(result));
  }
}
