# Alexa+ Remote Evidence

Status: **PASS**

Canonical production commit: `a7ac8e45411820ce8e222e9e9acf54760f0cc8d9`

Production MCP: `https://ripple-v12-production.up.railway.app/mcp`

## 1. Authenticated MCP + Alexa OAuth refresh proof

Remote smoke runner commit: `740b91c9f2cd1fe830387d35efe28910553a0438`

Railway deployment: `757947a8-6aea-4f6b-8e89-a28156da9456`

Observed runtime output:

```text
Ripple authenticated MCP smoke: PASS
protocol: 2025-11-25
oauth_refresh_without_resource: PASS
oauth_refresh_wrong_resource: rejected
preview: 5 impacts / 0 writes
approval writes: 0
execute: 5 receipts / 5 unique writes
replay: 5 deduplicated / 5 unique writes
```

This proves the Alexa-compatible refresh-token path over real HTTPS: refresh succeeds when Alexa omits the RFC 8707 `resource` parameter, while an explicitly wrong resource is rejected. The refreshed user token then completes the authenticated MCP repair flow without weakening the exact-approval or idempotency boundaries.

## 2. Alexa store-media remote proof

Railway smoke-runner deployment: `2a9a432e-2654-43fc-8f1f-f232878454bb`

Observed runtime output:

```text
Ripple Alexa store-media remote gate: PASS
carousel: 600x900 / exact sha256 / immutable / nosniff
privacy_terms: reachable and non-placeholder
icons: 6/6 exact dimensions
mcp: https://ripple-v12-production.up.railway.app/mcp
```

The gate verifies from outside the production service:

- carousel is a valid 600x900 PNG with the pinned SHA-256;
- `Content-Type` is PNG, caching is immutable, and `X-Content-Type-Options: nosniff` is present;
- privacy policy and terms URLs are reachable and contain substantive non-placeholder text;
- all six required icon sizes resolve as PNGs with exact dimensions: 64, 72, 88, 126, 180, and 241 px;
- the manifest points at the canonical production MCP endpoint.

## 3. Defect discovered by independent evidence runner

The first reproducible store-media run exposed a packaging defect: the shared Docker image omitted `addon-package/addon.json`, causing a runtime `FileNotFoundError` even though Railway showed the deployment lifecycle as `SUCCESS`.

The defect was fixed in PR #14 by copying `addon-package` into the Docker image and adding a CI invariant so the manifest cannot silently disappear from the image contract again.

Production deployment after that fix: `b68837f9-50e2-4d48-9604-68616ae72f78` — `SUCCESS` on commit `a7ac8e45411820ce8e222e9e9acf54760f0cc8d9`.

## Evidence rule

A Railway deployment status alone is not treated as functional proof. A gate is accepted only when the intended runtime assertions execute and emit the expected PASS output.