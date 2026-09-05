import { defineFn } from "@browserbasehq/sdk-functions";
import { chromium } from "playwright-core";

type Params = {
  connectUrl: string;
  url: string;
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
  assert(typeof params.url === "string" && params.url.length > 0, "params.url is required");

  const cdp = new URL(params.connectUrl);
  assert(cdp.protocol === "wss:", "connectUrl must use wss");
  assert(cdp.hostname.endsWith("browserbase.com"), "connectUrl must target Browserbase");

  const target = new URL(params.url);
  assert(["http:", "https:"].includes(target.protocol), "only HTTP(S) target URLs are allowed");

  const browser = await chromium.connectOverCDP(params.connectUrl);
  const browserContext = browser.contexts()[0];
  assert(browserContext, "target browser context is missing");
  const page = browserContext.pages()[0] ?? (await browserContext.newPage());
  const response = await page.goto(params.url, {
    waitUntil: "domcontentloaded",
    timeout: 120_000,
  });
  const finalUrl = page.url();

  // Deliberately do not call browser.close(): the target is a separately-created
  // keepAlive Browserbase session and must remain alive for human Live View login.
  return {
    ok: true,
    initialHttpStatus: response?.status() ?? null,
    awsAuthVerify: target.hostname.includes("aws.amazon.com") ? classifyAws(finalUrl) : undefined,
  };
});
