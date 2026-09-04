import { chromium } from 'playwright';

const brokerUrl = process.env.BROWSERBASE_BROKER_URL;
const rawCommand = process.env.BROWSER_COMMAND || '{"url":"https://example.com","sensitive":false,"steps":[{"action":"assertTitle","contains":"Example Domain"}]}';
const commandId = process.env.BROWSER_COMMAND_ID || 'initial';

function fail(message) {
  throw new Error(message);
}

function timeoutFor(step = {}, request = {}) {
  const raw = Number(step.timeoutMs ?? request.timeoutMs ?? 30_000);
  return Number.isFinite(raw) ? Math.max(1, Math.min(raw, 120_000)) : 30_000;
}

async function getRemoteSession() {
  if (!brokerUrl) fail('BROWSERBASE_BROKER_URL is missing');
  const response = await fetch(brokerUrl, {
    method: 'GET',
    redirect: 'follow',
    signal: AbortSignal.timeout(30_000),
  });
  const text = await response.text();
  if (!response.ok) fail(`Browser broker returned HTTP ${response.status}`);
  let body;
  try {
    body = JSON.parse(text);
  } catch {
    fail('Browser broker returned non-JSON response');
  }
  if (!body?.connectUrl) fail('Browser broker response is missing connectUrl');
  return body.connectUrl;
}

async function executeCommand() {
  let request;
  try {
    request = JSON.parse(rawCommand);
  } catch {
    fail('BROWSER_COMMAND is not valid JSON');
  }

  if (!request || typeof request !== 'object') fail('Browser command must be an object');
  if (typeof request.url !== 'string' || !request.url) fail('Browser command url is required');
  const parsed = new URL(request.url);
  if (!['http:', 'https:'].includes(parsed.protocol)) fail('Only HTTP(S) URLs are allowed');

  const steps = Array.isArray(request.steps) ? request.steps : [];
  if (steps.length > 40) fail('Maximum 40 browser steps');
  const sensitive = request.sensitive !== false;

  const result = {
    ok: false,
    commandId,
    sensitive,
    stepCount: steps.length,
    startedAt: new Date().toISOString(),
    steps: [],
  };

  let browser;
  try {
    const connectUrl = await getRemoteSession();
    browser = await chromium.connectOverCDP(connectUrl);
    const contexts = browser.contexts();
    if (!contexts.length) fail('Remote browser has no context');
    const context = contexts[0];
    const page = context.pages()[0] || await context.newPage();

    const response = await page.goto(request.url, {
      waitUntil: request.waitUntil || 'domcontentloaded',
      timeout: timeoutFor({}, request),
    });
    result.initialHttpStatus = response?.status() ?? null;

    for (let i = 0; i < steps.length; i += 1) {
      const step = steps[i];
      const action = String(step?.action || '');
      if (!action) fail(`Step ${i + 1}: action is required`);
      const item = { index: i + 1, action, ok: false };

      switch (action) {
        case 'click':
          if (!step.selector) fail(`Step ${i + 1}: selector is required`);
          await page.locator(step.selector).click({ timeout: timeoutFor(step, request) });
          break;
        case 'fill':
          if (!step.selector) fail(`Step ${i + 1}: selector is required`);
          await page.locator(step.selector).fill(String(step.value ?? ''), { timeout: timeoutFor(step, request) });
          break;
        case 'press':
          if (!step.selector || !step.key) fail(`Step ${i + 1}: selector and key are required`);
          await page.locator(step.selector).press(String(step.key), { timeout: timeoutFor(step, request) });
          break;
        case 'check':
          if (!step.selector) fail(`Step ${i + 1}: selector is required`);
          await page.locator(step.selector).check({ timeout: timeoutFor(step, request) });
          break;
        case 'selectOption':
          if (!step.selector) fail(`Step ${i + 1}: selector is required`);
          await page.locator(step.selector).selectOption(step.value, { timeout: timeoutFor(step, request) });
          break;
        case 'waitForSelector':
          if (!step.selector) fail(`Step ${i + 1}: selector is required`);
          await page.locator(step.selector).waitFor({ state: step.state || 'visible', timeout: timeoutFor(step, request) });
          break;
        case 'waitForTimeout':
          await page.waitForTimeout(Math.max(0, Math.min(Number(step.ms || 0), 10_000)));
          break;
        case 'assertText': {
          if (!step.selector) fail(`Step ${i + 1}: selector is required`);
          const text = (await page.locator(step.selector).textContent({ timeout: timeoutFor(step, request) })) ?? '';
          if (step.equals !== undefined && text.trim() !== String(step.equals)) fail(`Step ${i + 1}: text equality assertion failed`);
          if (step.contains !== undefined && !text.includes(String(step.contains))) fail(`Step ${i + 1}: text contains assertion failed`);
          if (!sensitive) item.observedText = text.trim().slice(0, 500);
          break;
        }
        case 'assertTitle': {
          const title = await page.title();
          if (step.equals !== undefined && title !== String(step.equals)) fail(`Step ${i + 1}: title equality assertion failed`);
          if (step.contains !== undefined && !title.includes(String(step.contains))) fail(`Step ${i + 1}: title contains assertion failed`);
          if (!sensitive) item.observedTitle = title;
          break;
        }
        case 'assertUrl': {
          const url = page.url();
          if (step.equals !== undefined && url !== String(step.equals)) fail(`Step ${i + 1}: URL equality assertion failed`);
          if (step.contains !== undefined && !url.includes(String(step.contains))) fail(`Step ${i + 1}: URL contains assertion failed`);
          if (!sensitive) item.observedUrl = url;
          break;
        }
        default:
          fail(`Step ${i + 1}: unsupported action ${action}`);
      }

      item.ok = true;
      result.steps.push(item);
    }

    result.ok = true;
    if (!sensitive) {
      result.finalUrl = page.url();
      result.title = await page.title();
    }
    result.finishedAt = new Date().toISOString();
    return result;
  } finally {
    await browser?.close();
  }
}

let output;
try {
  output = await executeCommand();
} catch (error) {
  output = {
    ok: false,
    commandId,
    error: error instanceof Error ? error.message : String(error),
    finishedAt: new Date().toISOString(),
  };
}

console.log(`BROWSER_WORKER_RESULT ${JSON.stringify(output)}`);

// Keep the Railway worker healthy after executing one command. Updating
// BROWSER_COMMAND_ID/BROWSER_COMMAND triggers a fresh deploy and a fresh run.
setInterval(() => {}, 60_000);
