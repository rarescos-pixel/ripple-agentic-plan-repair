# Free Work Replacement Browser Runner

Status: validated on branch `poc/free-work-replacement`.

## Purpose

Provide a free-first browser execution layer that ChatGPT can drive without requiring the user to run a terminal or manually shuttle browser state. Keep the browser work isolated from Ripple production on `main`.

## Current architecture

There are now two complementary execution paths.

### 1. Local / public browser work

`ChatGPT -> GitHub connector -> POC branch request -> GitHub Actions -> Playwright/Chromium -> sanitized result/artifact -> ChatGPT`

This path is zero-cost, deterministic, and best for public or unauthenticated work.

### 2. Persistent authenticated browser work

`ChatGPT -> private Make on-demand scenario -> Browserbase Functions API -> managed Browserbase session -> persistent Browserbase Context -> private Make result -> ChatGPT`

The Browserbase API key is stored in Make's API-key credential store and is not committed to GitHub or pasted into chat. The persistent Context state itself remains server-side in Browserbase. The Context identifier is operational metadata and may appear in the POC source; it is not sufficient to access the stored browser state without valid Browserbase authorization.

## GitHub command path

1. Update `automation/browser-request.json` on branch `poc/free-work-replacement`.
2. The push triggers `.github/workflows/free-work-replacement-poc.yml`.
3. GitHub Actions runs the Playwright runner.
4. The runner uses local Chromium or an optional Browserbase provider.
5. The workflow writes sanitized `result.json` and, only for explicitly non-sensitive requests, optional screenshots.
6. ChatGPT can inspect workflow runs and artifacts through the GitHub connector.

The request file is therefore a lightweight command bus from ChatGPT to a real browser.

## Local runner actions

The established GitHub Actions runner supports browser navigation/interactions including click, fill, press, check, select, upload, wait, assertions, and non-sensitive screenshots. Sensitive requests suppress page observations and artifacts.

## Browserbase Functions

Browserbase Functions provide the cleaner cloud execution path because Browserbase creates the managed browser session for each invocation and the function connects to it over Playwright CDP.

### Generic function

A generic Browserbase action runner was successfully built, published, and invoked against `https://example.com`. The real invocation returned HTTP 200, `ok: true`, and verified the page title `Example Domain`.

### Persistent authenticated function

A separate function is configured with Browserbase `sessionConfig` using a persistent Context (`persist: true`). The Context is server-side Browserbase state; no login cookies are committed to the repository.

AWS authentication persistence has been verified across distinct Browserbase sessions. Two separate invocations navigated to authenticated AWS Console pages and each returned:

- invocation status `COMPLETED`;
- HTTP 200;
- `ok: true`;
- `authenticated: true`.

The second verification targeted the IAM console, proving the result was not merely the same live browser session surviving from the first invocation.

### Persistent read-only runner

`browserbase_function/persistent_runner.ts` is intentionally restricted to read-only browser operations while attached to the authenticated persistent Context. Its allowed operations are navigation, waits, assertions, targeted text reads, and targeted attribute reads. Generic authenticated click/fill/write capabilities are deliberately not enabled in this persistent runner.

The package is now independently validated with the official Browserbase Functions CLI dry-run path. GitHub Actions run `33908767299` completed successfully: checkout, frozen-lockfile install, and `bb publish persistent_runner.ts --dry-run` all passed. This proves the current package/entrypoint is structurally publishable with Browserbase Functions SDK `1.0.1`.

A previously submitted remote Browserbase build for this richer runner has build id `9502412c-244a-42d9-ba31-b8e4ed62efff`. Its final remote status still needs to be read through an authenticated Browserbase API path before that remote deployment is marked canonical.

## Private Make command bus

The free Make plan permits only two active scenarios in the private space, so the active slots are reserved for the runtime path rather than build tooling.

Intended runtime scenarios:

- `Browserbase Persistent Readonly Invoke - Private`
- `Browserbase Invocation Status - Private`

The invocation scenario accepts a target URL, an expected authenticated URL fragment, and a sensitive-mode flag. It invokes the persistent Browserbase Function without editing a scenario for every request. The status scenario accepts an invocation ID and returns the Browserbase invocation result.

This pair was previously verified end-to-end against the authenticated AWS IAM console: invoke -> Browserbase managed session -> persistent Context -> completed result -> status retrieval.

The older generic API bridge and Browserbase Function publisher remain non-runtime tooling and should stay inactive except during publishing or diagnosis.

### ChatGPT connector state

The Make app was reinstalled/reconnected in ChatGPT on 2026-09-04. The app catalog reports it installed and enabled, but direct Make tool invocations in the same conversation currently fail at the ChatGPT tool-routing layer with `Resource not found` even after successful rediscovery of the Make tool schemas. Treat this as a connector/tool-routing blocker, not as evidence that the Make scenarios or Browserbase credential were deleted.

Do not rebuild the Browserbase credential or re-enter the API key merely because of this ChatGPT routing failure.

## Browserbase free-plan constraint

Current Browserbase free-plan research indicates one concurrent browser and 60 browser minutes per month, with no card required. Browser time must therefore be used only when persistent cloud state or interactive browser execution is actually needed; public deterministic work should stay on GitHub Actions/local Chromium.

Browserbase Contexts persist independently from a single browser session, but individual websites can still expire or revoke their own cookies/tokens.

## Sensitive mode

Authenticated/private work defaults to sensitive output suppression. Do not expose broad page content unless a task explicitly requires a narrow read and the selector/output has been audited.

Never commit passwords, API tokens, cookies, session storage, private form contents, or authentication snapshots to this public repository.

## Security boundary

- Browserbase API key: Make credential store only for the current private Functions path.
- Browserbase Context state: server-side Browserbase state.
- Login/MFA: user may need to perform unavoidable authentication manually in Browserbase Live View when a site invalidates the stored session.
- Public GitHub artifacts: disabled for sensitive authenticated work.
- Authenticated mutation: not generalized into the persistent runner. Any future write path must be target-specific and separately audited.

## Verified evidence

### Browser launch / navigation / screenshot

GitHub Actions run `33875581489` succeeded against `https://example.com`, returned HTTP 200/title `Example Domain`, and produced a screenshot artifact.

### Form fill / file upload / click / assertion

Run `33875968084` succeeded against the local fixture, including field fill, upload, Submit, text assertion, screenshots, and machine-readable result.

### Chat-to-browser command bus

Commit `4ffd385290ce957fb94e38dbd912d0e453b548d2` changed the request to `https://example.com`; run `33876105352` then executed automatically and succeeded.

### Provider/security regression

Run `33877930336` succeeded after the Browserbase provider and sensitive-mode guardrails were added, proving that the local path remained functional.

### Browserbase Function invocation

The generic Browserbase Function was built and invoked successfully against `https://example.com`, returning `COMPLETED`, HTTP 200 and `ok: true`.

### Persistent AWS authentication

Separate managed Browserbase sessions using the same persistent Context both reached authenticated AWS Console locations and returned `authenticated: true`. A later invocation through the reusable private Make invoke/status pair also completed successfully against AWS IAM.

### Persistent read-only package validation

Run `33908767299` completed successfully and validates the current `persistent_runner.ts` package through Browserbase CLI dry-run using the frozen lockfile.

## Production isolation audit

Browser automation work remains on `poc/free-work-replacement`. The Browserbase example request file is present on the POC branch and was explicitly checked as absent from `main`.

Functional browser-code milestone: `ce556d067fafc0f8858269231be75ad001745bf9` (`Restrict persistent Browserbase runner to read-only actions`). Later validation/documentation commits advance the branch head beyond this SHA.

Do not merge this branch wholesale into `main`; it has diverged from production and must be retargeted/audited before any selective production change.

## Canonical files

- `.github/workflows/free-work-replacement-poc.yml`
- `.github/workflows/browserbase-function-validate.yml`
- `scripts/browser_runner.mjs`
- `scripts/browser_bridge_runner.mjs`
- `automation/browser-request.json`
- `browserbase_function/index.ts`
- `browserbase_function/persistent.ts`
- `browserbase_function/persistent_runner.ts`
- `browserbase_function/package.json`
- `browserbase_function/pnpm-lock.yaml`
- `docs/FREE_WORK_REPLACEMENT.md`

## Next gate

1. Recover direct ChatGPT -> Make tool invocation without rebuilding credentials.
2. Read remote build `9502412c-244a-42d9-ba31-b8e4ed62efff`.
3. If `COMPLETED`, point the reusable private Make invoke scenario at the new read-only Function ID and expose a safe `steps` input schema.
4. Verify one targeted authenticated `readText` operation with sensitive output controls.
5. Keep the local GitHub Actions path as the default for public browser work to conserve Browserbase minutes.
