# Free Work Replacement Browser Runner

Status: validated on branch `poc/free-work-replacement`.

## Purpose

Use GitHub Actions + Playwright as a zero-cost browser execution layer that can be driven from ChatGPT through the GitHub connector without touching `main` or Railway production.

## Command path

1. Update `automation/browser-request.json` on branch `poc/free-work-replacement`.
2. The push automatically triggers `.github/workflows/free-work-replacement-poc.yml`.
3. GitHub Actions runs `scripts/browser_runner.mjs` in headless Chromium.
4. The workflow writes `result.json` plus screenshots/downloads to a GitHub Actions artifact.
5. ChatGPT can inspect the workflow run and artifact through the GitHub connector.

This makes the request file a lightweight command bus from ChatGPT to a real cloud browser.

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
- `screenshot`

A request may contain up to 30 steps. HTTP and HTTPS target URLs are accepted.

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

## Security boundary

The repository is public. Never put passwords, tokens, cookies, session state, private form contents, or other secrets directly in `automation/browser-request.json` or any committed file.

The runner supports `valueFromEnv` so sensitive field values can come from environment variables instead of the request file. Authenticated browser work is not considered fully solved until a secure secret/session provisioning path is configured.

## Production isolation

The runner is isolated on `poc/free-work-replacement`. It is intentionally not merged into `main`, because Railway production watches the repository's `main` branch. Browser automation changes must not trigger application deployment accidentally.

## Canonical files

- `.github/workflows/free-work-replacement-poc.yml`
- `scripts/browser_runner.mjs`
- `automation/browser-request.json`
- `fixtures/browser-automation/form.html`
- `fixtures/browser-automation/upload.txt`
