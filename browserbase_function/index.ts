import { defineFn } from "@browserbasehq/sdk-functions";
import { chromium } from "playwright-core";

type Step = {
  action: string;
  selector?: string;
  value?: string | string[];
  key?: string;
  url?: string;
  ms?: number;
  state?: "attached" | "detached" | "visible" | "hidden";
  equals?: string;
  contains?: string;
  timeoutMs?: number;
};

type Request = {
  url: string;
  waitUntil?: "load" | "domcontentloaded" | "networkidle" | "commit";
  timeoutMs?: number;
  sensitive?: boolean;
  steps?: Step[];
};

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function timeoutFor(step: Step = { action: "" }, request: Request): number {
  const raw = Number(step.timeoutMs ?? request.timeoutMs ?? 30_000);
  return Number.isFinite(raw) ? Math.max(1, Math.min(raw, 120_000)) : 30_000;
}

defineFn("free-work-browser-runner", async (context, rawParams) => {
  const request = rawParams as Request;
  assert(request && typeof request === "object", "params must be an object");
  assert(typeof request.url === "string" && request.url.length > 0, "params.url is required");

  const parsed = new URL(request.url);
  assert(["http:", "https:"].includes(parsed.protocol), "only HTTP(S) URLs are allowed");

  const steps = Array.isArray(request.steps) ? request.steps : [];
  assert(steps.length <= 40, "maximum 40 steps");
  const sensitive = request.sensitive !== false;

  const browser = await chromium.connectOverCDP(context.session.connectUrl);
  try {
    const browserContext = browser.contexts()[0];
    assert(browserContext, "managed browser context is missing");
    const page = browserContext.pages()[0] ?? (await browserContext.newPage());

    const navigation = await page.goto(request.url, {
      waitUntil: request.waitUntil ?? "domcontentloaded",
      timeout: timeoutFor({ action: "" }, request),
    });

    const result: Record<string, unknown> = {
      ok: false,
      sensitive,
      initialHttpStatus: navigation?.status() ?? null,
      stepCount: steps.length,
      steps: [],
    };
    const stepResults = result.steps as Array<Record<string, unknown>>;

    for (let index = 0; index < steps.length; index += 1) {
      const step = steps[index];
      assert(step && typeof step === "object", `step ${index + 1} must be an object`);
      const action = String(step.action || "");
      assert(action, `step ${index + 1}: action is required`);
      const item: Record<string, unknown> = { index: index + 1, action, ok: false };

      switch (action) {
        case "goto": {
          assert(step.url, `step ${index + 1}: url is required`);
          const target = new URL(step.url);
          assert(["http:", "https:"].includes(target.protocol), `step ${index + 1}: only HTTP(S) URLs are allowed`);
          await page.goto(step.url, { waitUntil: "domcontentloaded", timeout: timeoutFor(step, request) });
          break;
        }
        case "click":
          assert(step.selector, `step ${index + 1}: selector is required`);
          await page.locator(step.selector).click({ timeout: timeoutFor(step, request) });
          break;
        case "fill":
          assert(step.selector, `step ${index + 1}: selector is required`);
          await page.locator(step.selector).fill(String(step.value ?? ""), { timeout: timeoutFor(step, request) });
          break;
        case "press":
          assert(step.selector && step.key, `step ${index + 1}: selector and key are required`);
          await page.locator(step.selector).press(step.key, { timeout: timeoutFor(step, request) });
          break;
        case "check":
          assert(step.selector, `step ${index + 1}: selector is required`);
          await page.locator(step.selector).check({ timeout: timeoutFor(step, request) });
          break;
        case "selectOption":
          assert(step.selector, `step ${index + 1}: selector is required`);
          await page.locator(step.selector).selectOption(step.value ?? "", { timeout: timeoutFor(step, request) });
          break;
        case "waitForSelector":
          assert(step.selector, `step ${index + 1}: selector is required`);
          await page.locator(step.selector).waitFor({ state: step.state ?? "visible", timeout: timeoutFor(step, request) });
          break;
        case "waitForTimeout":
          await page.waitForTimeout(Math.max(0, Math.min(Number(step.ms ?? 0), 10_000)));
          break;
        case "assertText": {
          assert(step.selector, `step ${index + 1}: selector is required`);
          const text = (await page.locator(step.selector).textContent({ timeout: timeoutFor(step, request) })) ?? "";
          if (step.equals !== undefined) assert(text.trim() === String(step.equals), `step ${index + 1}: text equality assertion failed`);
          if (step.contains !== undefined) assert(text.includes(String(step.contains)), `step ${index + 1}: text contains assertion failed`);
          if (!sensitive) item.observedText = text.trim().slice(0, 500);
          break;
        }
        case "assertTitle": {
          const title = await page.title();
          if (step.equals !== undefined) assert(title === String(step.equals), `step ${index + 1}: title equality assertion failed`);
          if (step.contains !== undefined) assert(title.includes(String(step.contains)), `step ${index + 1}: title contains assertion failed`);
          if (!sensitive) item.observedTitle = title;
          break;
        }
        case "assertUrl": {
          const current = page.url();
          if (step.equals !== undefined) assert(current === String(step.equals), `step ${index + 1}: URL equality assertion failed`);
          if (step.contains !== undefined) assert(current.includes(String(step.contains)), `step ${index + 1}: URL contains assertion failed`);
          if (!sensitive) item.observedUrl = current;
          break;
        }
        default:
          throw new Error(`step ${index + 1}: unsupported action ${action}`);
      }

      item.ok = true;
      stepResults.push(item);
    }

    result.ok = true;
    if (!sensitive) {
      result.finalUrl = page.url();
      result.title = await page.title();
    }
    return result;
  } finally {
    await browser.close();
  }
});
