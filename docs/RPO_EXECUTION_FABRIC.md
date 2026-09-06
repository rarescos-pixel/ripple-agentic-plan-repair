# RPO Execution Fabric v1

Purpose: reproduce the useful execution properties of ChatGPT Work without forcing every task through Work, while preserving security, auditability, low cost and cumulative learning.

## Default routing

1. Direct connector/API.
2. Programmatic cloud execution (GitHub Actions, OIDC, provider APIs).
3. Reusable browser control on the authenticated local Opera session.
4. ChatGPT Work only when it supplies a distinct capability not available above.
5. Human intervention only for irreducible consent/MFA/local installation/subjective decision.

The user must not be used as a mouse, terminal, copy/paste relay or debugging transport when a working programmatic route exists.

## Execution lanes

### API lane
Use connected tools for Gmail, Calendar, GitHub, Railway, Files/Library and other supported services. Prefer structured APIs over GUI automation.

### Cloud lane
Use GitHub Actions as the default ephemeral terminal/build/test environment. Use GitHub OIDC for AWS. Do not create long-lived AWS keys as a workaround. Every consequential cloud change requires a read-back or smoke test.

### Browser lane
Use Opera Connector for page state, tabs, screenshots and navigation. Use OAI Browser Control Bridge only when UI interaction is actually required. Never transmit passwords, MFA, cookies, access tokens or other secrets through the browser command channel.

### Local lane
Local filesystem/terminal automation is DEFERRED by default. Do not request installation of local agents unless a concrete task cannot be completed with GitHub, Files/Library, Railway, APIs or Work. The user's presence at the PC is a scarce resource.

### Work fallback lane
Use ChatGPT Work when the task specifically needs a persistent cloud browser/computer, authenticated browser work while the user's PC is off, or another capability absent from the lanes above. Work is a fallback capability, not the default location for complex work.

## Browser Bridge lifecycle

Current v1 is VERIFIED but bounded. A future v2 is justified only by a concrete recurring browser requirement and should add: short-lived signed commands, semantic role/name targeting, wait/assert primitives, bounded retries, state transitions, close/switch tab, and sanitized receipts. Do not require a reinstall merely to perfect infrastructure.

## State model

For every critical capability use one of:

- UNKNOWN
- AVAILABLE
- VERIFIED_WORKING
- DEGRADED
- DEFERRED
- INVALIDATED
- UNAVAILABLE

Consult `.rpo/capability-ledger.json` before inventing a workaround. VERIFIED_WORKING capabilities are reused first. INVALIDATED paths are not retried without new evidence.

## Task state

Operational tasks should converge through:

`QUEUED -> RUNNING -> WAITING_USER (only if irreducible) -> VERIFYING -> DONE | FAILED`

A FAILED state must record the exact sanitized failure class. Retry is allowed only if the next attempt changes the hypothesis, instrumentation or execution route.

## Verification contract

A successful command is not automatically a successful objective. DONE requires an observable state read-back or independent smoke test. Examples:

- AWS auth: `sts:GetCallerIdentity`
- AWS configuration: describe/read-back the exact resource
- Railway deploy: deployment status plus runtime smoke when relevant
- GitHub change: fetch resulting file/commit/status
- Browser action: assert expected text/URL/page state

## Cost discipline

Optimize total cost: money + credits + user attention + elapsed time + operational risk + future complexity. Tooling is stopped as soon as the blocker it was built for is removed. Ripple's AWS operational target remains zero cost; alert/budget thresholds are guardrails, not permission to spend.

## Canonical current decisions

- GitHub Actions is the default cloud terminal.
- GitHub OIDC is the canonical AWS authentication path.
- Railway is a direct runtime/deployment lane through its connector.
- Opera/Browser Bridge is reserved for UI-only work.
- Remote Desktop Commander/local setup is DEFERRED.
- Persistent authenticated browser work with the PC off remains a ChatGPT Work fallback.
- No rediscovery of Browserbase/Railway-browser/remote-login paths unless a new requirement invalidates this architecture.
