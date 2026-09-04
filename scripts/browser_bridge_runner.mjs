import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const requestPath = process.env.BROWSER_REQUEST_PATH || 'automation/browser-request.json';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/browser-runner';
const resultPath = path.join(artifactDir, 'result.json');

await fs.mkdir(artifactDir, { recursive: true });

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function nonEmpty(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

let browser;
let keepSessionOpen = false;
let result = {
  ok: false,
  provider: 'browserbase-bridge',
  requestPath,
  startedAt: new Date().toISOString(),
};

try {
  const request = JSON.parse(await fs.readFile(requestPath, 'utf8'));
  keepSessionOpen = request.keepSessionOpen === true;
  assert(request.provider === 'browserbase-bridge', 'Request provider must be browserbase-bridge');
  assert(nonEmpty(request.bridgeUrl), 'bridgeUrl is required');
  assert(nonEmpty(request.url), 'url is required');

  const bridgeResponse = await fetch(request.bridgeUrl, {
    method: 'GET',
    redirect: 'follow',
    headers: { 'accept': 'application/json' },
  });
  const bridgeText = await bridgeResponse.text();
  assert(bridgeResponse.ok, `Browserbase bridge returned HTTP ${bridgeResponse.status}`);

  let session;
  try {
    session = JSON.parse(bridgeText);
  } catch {
    throw new Error('Browserbase bridge did not return JSON');
  }
  assert(nonEmpty(session?.connectUrl), 'Browserbase bridge response is missing connectUrl');
  assert(nonEmpty(session?.id), 'Browserbase bridge response is missing session id');

  browser = await chromium.connectOverCDP(session.connectUrl);
  const contexts = browser.contexts();
  assert(contexts.length > 0, 'Browserbase session has no browser context');
  const context = contexts[0];
  let page = context.pages()[0];
  if (!page) page = await context.newPage();

  const response = await page.goto(request.url, {
    waitUntil: request.waitUntil || 'domcontentloaded',
    timeout: Math.min(Number(request.timeoutMs || 60_000), 120_000),
  });

  const expected = String(request.authenticatedUrlContains || '').trim();
  const holdMs = Math.max(0, Math.min(Number(request.holdMs || 0), 240_000));
  const deadline = Date.now() + holdMs;
  let authenticated = expected ? page.url().includes(expected) : true;

  while (!authenticated && Date.now() < deadline) {
    await page.waitForTimeout(2_000);
    authenticated = page.url().includes(expected);
  }

  if (expected && !authenticated) {
    throw new Error(`Authentication target not reached before timeout: ${expected}`);
  }

  result = {
    ...result,
    ok: true,
    sessionId: session.id,
    contextId: session.contextId || null,
    initialHttpStatus: response?.status() ?? null,
    authenticated,
    matchedUrlFragment: expected || null,
    keepSessionOpen,
    finishedAt: new Date().toISOString(),
  };
} catch (error) {
  result = {
    ...result,
    ok: false,
    error: error instanceof Error ? error.message : String(error),
    keepSessionOpen,
    finishedAt: new Date().toISOString(),
  };
  process.exitCode = 1;
} finally {
  try {
    if (!keepSessionOpen) {
      await browser?.close();
    }
  } finally {
    await fs.writeFile(resultPath, JSON.stringify(result, null, 2) + '\n', 'utf8');
    console.log(JSON.stringify(result));
  }
}

if (keepSessionOpen) {
  process.exit(process.exitCode || 0);
}
