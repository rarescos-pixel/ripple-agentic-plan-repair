import { defineFn } from "@browserbasehq/sdk-functions";
import { chromium } from "playwright-core";

type Params = {
  connectUrl: string;
  url?: string;
  email?: string;
  clickNext?: boolean;
};

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function classifyAws(finalUrl: string) {
  try {
    const u = new URL(finalUrl);
    const host = u.hostname.toLowerCase();
    const path = u.pathname.toLowerCase();
    const signin = host === "signin.aws.amazon.com" || host.endsWith(".signin.aws.amazon.com");
    const consoleHost = host === "console.aws.amazon.com" || host.endsWith(".console.aws.amazon.com");
    return {
      signedIn: consoleHost && !signin,
      cloudShellReached: consoleHost && path.includes("/cloudshell"),
      hostClass: signin ? "signin" : consoleHost ? "console" : "other",
    };
  } catch {
    return { signedIn: false, cloudShellReached: false, hostClass: "invalid" };
  }
}

defineFn("free-work-navigate-existing-session", async (_context, rawParams) => {
  const params = rawParams as Params;
  assert(params && typeof params === "object", "params must be an object");
  assert(typeof params.connectUrl === "string" && params.connectUrl.length > 0, "params.connectUrl is required");

  const cdp = new URL(params.connectUrl);
  assert(cdp.protocol === "wss:", "connectUrl must use wss");
  assert(cdp.hostname.endsWith("browserbase.com"), "connectUrl must target Browserbase");

  const browser = await chromium.connectOverCDP(params.connectUrl);
  const browserContext = browser.contexts()[0];
  assert(browserContext, "target browser context is missing");
  const page = browserContext.pages()[0] ?? (await browserContext.newPage());

  let initialHttpStatus: number | null = null;
  if (params.url) {
    const target = new URL(params.url);
    assert(["http:", "https:"].includes(target.protocol), "only HTTP(S) target URLs are allowed");
    const response = await page.goto(params.url, {
      waitUntil: "domcontentloaded",
      timeout: 120_000,
    });
    initialHttpStatus = response?.status() ?? null;
  }

  let emailFilled = false;
  let nextClicked = false;
  if (params.email) {
    const candidates = [
      'input[type="email"]',
      'input[name="email"]',
      'input[name="username"]',
      '#resolving_input',
      'input[autocomplete="username"]',
      'input[type="text"]',
    ];
    for (const selector of candidates) {
      const loc = page.locator(selector).first();
      if (await loc.isVisible().catch(() => false)) {
        await loc.fill(params.email);
        emailFilled = true;
        break;
      }
    }
    assert(emailFilled, "email field not found");
  }

  if (params.clickNext) {
    const nextCandidates = [
      page.getByRole('button', { name: /next|continue|sign in/i }).first(),
      page.locator('button[type="submit"]').first(),
      page.locator('input[type="submit"]').first(),
    ];
    for (const loc of nextCandidates) {
      if (await loc.isVisible().catch(() => false)) {
        await loc.click();
        nextClicked = true;
        break;
      }
    }
    assert(nextClicked, "next/continue button not found");
    await page.waitForTimeout(1200);
  }

  const finalUrl = page.url();
  return {
    ok: true,
    initialHttpStatus,
    emailFilled,
    nextClicked,
    awsAuthVerify: finalUrl.includes("aws.amazon.com") ? classifyAws(finalUrl) : undefined,
  };
});
