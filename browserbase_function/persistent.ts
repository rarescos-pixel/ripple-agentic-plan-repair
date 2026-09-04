import { defineFn } from "@browserbasehq/sdk-functions";
import { chromium } from "playwright-core";

type Params = {
  url: string;
  sensitive?: boolean;
  titleContains?: string;
  urlContains?: string;
};

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

defineFn(
  "free-work-persistent-browser",
  async (context, rawParams) => {
    const params = rawParams as Params;
    assert(params && typeof params === "object", "params must be an object");
    assert(typeof params.url === "string" && params.url.length > 0, "params.url is required");

    const target = new URL(params.url);
    assert(["http:", "https:"].includes(target.protocol), "only HTTP(S) URLs are allowed");

    const sensitive = params.sensitive !== false;
    const browser = await chromium.connectOverCDP(context.session.connectUrl);
    try {
      const browserContext = browser.contexts()[0];
      assert(browserContext, "managed browser context is missing");
      const page = browserContext.pages()[0] ?? (await browserContext.newPage());
      const response = await page.goto(params.url, {
        waitUntil: "domcontentloaded",
        timeout: 120_000,
      });

      const finalUrl = page.url();
      const title = await page.title();
      if (params.titleContains) {
        assert(title.includes(params.titleContains), "title assertion failed");
      }
      if (params.urlContains) {
        assert(finalUrl.includes(params.urlContains), "URL assertion failed");
      }

      return {
        ok: true,
        authenticated: params.urlContains ? finalUrl.includes(params.urlContains) : undefined,
        initialHttpStatus: response?.status() ?? null,
        sensitive,
        ...(sensitive ? {} : { finalUrl, title }),
      };
    } finally {
      await browser.close();
    }
  },
  {
    sessionConfig: {
      region: "eu-central-1",
      browserSettings: {
        context: {
          id: "78211c23-8511-4c33-899d-a7c7f27fdf2e",
          persist: true,
        },
      },
    },
  },
);
