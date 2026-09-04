import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const brokerUrl = process.env.BROWSERBASE_BROKER_URL;
const resultPath = 'browserbase-persistence-result.json';
const markerKey = 'work-replacement-persistence-marker';
const markerValue = `verified-${process.env.GITHUB_RUN_ID || Date.now()}`;

if (!brokerUrl) throw new Error('BROWSERBASE_BROKER_URL is required');

async function createSessionViaBroker() {
  const response = await fetch(brokerUrl, {
    method: 'GET',
    redirect: 'follow',
    signal: AbortSignal.timeout(30_000),
  });
  const text = await response.text();
  if (!response.ok) throw new Error(`Broker returned HTTP ${response.status}`);

  let body;
  try {
    body = JSON.parse(text);
  } catch {
    throw new Error('Broker response was not JSON');
  }

  if (!body?.connectUrl) throw new Error('Broker response did not contain connectUrl');
  return { connectUrl: body.connectUrl, sessionId: body.id || null };
}

async function withSession(fn) {
  const session = await createSessionViaBroker();
  const browser = await chromium.connectOverCDP(session.connectUrl);
  try {
    const contexts = browser.contexts();
    if (!contexts.length) throw new Error('Remote session has no context');
    const context = contexts[0];
    const page = context.pages()[0] || await context.newPage();
    return await fn(page, session.sessionId);
  } finally {
    await browser.close();
  }
}

const startedAt = new Date().toISOString();
const result = {
  ok: false,
  test: 'browserbase-context-persistence',
  origin: 'https://example.com',
  startedAt,
};

try {
  await withSession(async (page) => {
    await page.goto('https://example.com', { waitUntil: 'domcontentloaded', timeout: 30_000 });
    await page.evaluate(({ key, value }) => localStorage.setItem(key, value), {
      key: markerKey,
      value: markerValue,
    });
    const observed = await page.evaluate((key) => localStorage.getItem(key), markerKey);
    if (observed !== markerValue) throw new Error('Marker was not written in session 1');
  });

  await new Promise((resolve) => setTimeout(resolve, 5000));

  let observedAfterReconnect = null;
  await withSession(async (page) => {
    await page.goto('https://example.com', { waitUntil: 'domcontentloaded', timeout: 30_000 });
    observedAfterReconnect = await page.evaluate((key) => localStorage.getItem(key), markerKey);
  });

  if (observedAfterReconnect !== markerValue) {
    throw new Error('Persistent context did not retain localStorage across sessions');
  }

  Object.assign(result, {
    ok: true,
    persistedAcrossFreshSessions: true,
    finishedAt: new Date().toISOString(),
  });
} catch (error) {
  Object.assign(result, {
    ok: false,
    error: error instanceof Error ? error.message : String(error),
    finishedAt: new Date().toISOString(),
  });
  process.exitCode = 1;
} finally {
  await fs.writeFile(resultPath, JSON.stringify(result, null, 2) + '\n', 'utf8');
  console.log(JSON.stringify(result));
}
