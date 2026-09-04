# Free Work Replacement Browser Runner

Status: validated on branch `poc/free-work-replacement`.

## Purpose

Use GitHub Actions + Playwright as a zero-cost browser execution layer that can be driven from ChatGPT through the GitHub connector without touching `main` or Railway production.

## Command path

1. Update `automation/browser-request.json` on branch `poc/free-work-replacement`.
2. The push automatically triggers `.github/workflows/free-work-replacement-poc.yml`.
3. GitHub Actions runs `scripts/browser_runner.mjs`.
4. The runner uses either local headless Chromium or an optional Browserbase cloud browser provider.
5. The workflow writes a sanitized `result.json` and, only for explicitly non-sensitive requests, optional screenshots to a GitHub Actions artifact.
6. ChatGPT can inspect the workflow run and artifact through the GitHub connector.

This makes the request file a lightweight command bus from ChatGPT to a real browser.

## Supported actions

- `click`
- `fill`
- `press`
- `check`
- `selectOption`
- `setInputFiles`
- `waitForSelector`
- `waitForTimeout`
- `assertText`
- `assertTitle`
- `assertUrl`
- `screenshot` (non-sensitive requests only)

A request may contain up to 30 steps. HTTP and HTTPS target URLs are accepted.

## Providers

### local

Default zero-cost mode. GitHub Actions launches headless Chromium on the runner. Suitable for public/non-authenticated browser work and deterministic tests.

### browserbase

Optional persistent authenticated cloud mode. The runner can create/connect to a Browserbase session over CDP and reuse a Browserbase Context with `persist: true`.

Request shape:

```json
{
  "provider": "browserbase",
  "browserbase": {
    "contextId": "<context-id>",
    "persist": true,
    "apiKeyFromEnv": "BROWSERBASE_API_KEY"
  }
}
```

The API key must only come from a GitHub Actions secret. `BROWSERBASE_PROJECT_ID` and `BROWSERBASE_CONTEXT_ID` may optionally be supplied as repository variables instead of request fields.

Browserbase Free currently provides 1 browser hour/month, up to 3 concurrent browsers and 15 minutes/session. Browserbase Contexts persist independently of individual sessions and are documented as living indefinitely until explicitly deleted or invalidated, which makes them suitable for long-lived authentication state. The site being automated may still expire/revoke its own cookies or tokens.

## Sensitive mode

Authenticated/private work must set:

```json
{
  "sensitive": true,
  "allowArtifacts": false
}
```

When `sensitive=true` the runner:

- suppresses observed page text, titles and URLs from `result.json`;
- disables screenshots even if requested;
- never writes secret values supplied through `valueFromEnv` into the request or result;
- returns only operation status, provider/session metadata and non-content errors.

This is required because the Ripple repository is public.

## Verified evidence

### Browser launch / navigation / screenshot

Run `33875581489` completed successfully against `https://example.com`, returned HTTP 200 and title `Example Domain`, and produced a screenshot artifact.

### Form fill / file upload / click / assertion

Run `33875968084` completed successfully against the local test fixture. It:

- filled the name field with `Rares`;
- uploaded `fixtures/browser-automation/upload.txt`;
- clicked Submit;
- verified the text `Hello Rares; file=upload.txt`;
- produced screenshots and `result.json`.

### Chat-to-browser command bus

Commit `4ffd385290ce957fb94e38dbd912d0e453b548d2` changed only `automation/browser-request.json` to target `https://example.com`. That push automatically triggered run `33876105352`, which completed successfully with HTTP 200, title/text assertions, and screenshots.

### Provider/security regression gate

Run `33877930336` completed successfully after adding the Browserbase provider and sensitive-mode guardrails. This verifies that the existing local zero-cost path still works after the persistent-auth extension.

## Security boundary

Never put passwords, tokens, cookies, session state, private form contents, or other secrets directly in `automation/browser-request.json` or any committed file.

The runner supports `valueFromEnv` so sensitive field values can come from environment variables. The workflow is wired for `secrets.BROWSERBASE_API_KEY`; the secret itself is intentionally not present in the repository.

For real authenticated Browserbase use, the only unresolved setup requirement is provisioning the Browserbase account/API key into the GitHub Actions secret or another secure invocation bridge. Do not paste that API key into the repository or normal chat messages.

## Production isolation

The runner is isolated on `poc/free-work-replacement`. It is intentionally not merged into `main`, because Railway production watches the repository's `main` branch. Browser automation changes must not trigger application deployment accidentally.

## Canonical files

- `.github/workflows/free-work-replacement-poc.yml`
- `scripts/browser_runner.mjs`
- `automation/browser-request.json`
- `fixtures/browser-automation/form.html`
- `fixtures/browser-automation/upload.txt`
