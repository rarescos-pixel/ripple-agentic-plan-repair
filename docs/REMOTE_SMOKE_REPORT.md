# Ripple — Remote Authenticated MCP Smoke Report

**Status: PASS**

- Date: 2026-09-04
- Public endpoint: `https://ripple-v12-production.up.railway.app`
- MCP endpoint: `https://ripple-v12-production.up.railway.app/mcp`
- Protocol version: `2025-11-25`
- Source commit tested: `708f9861b48745ca6d04d67df0e7efa2d329c25e`
- GitHub Actions quality gate on that commit: run `33850775269` — `SUCCESS`
- Target server deployment used by the fresh smoke: Railway `91bb37ff-4501-433f-ba8a-7a6e0b2a6b18` — `SUCCESS`
- Fresh smoke-runner deployment: Railway `f8a7b7bd-f874-41a2-baa6-a3dc46143b1b` — `SUCCESS`
- Post-smoke canonical server redeploy on the same source commit: Railway `a4b4416a-36c0-4c93-ac4c-96a728b68ac6` — `SUCCESS`
- Runner retirement deployment: Railway `2e21dac5-abda-4350-a8d8-fa39deb32426` — `SUCCESS`

## Independent execution topology

The fresh smoke test ran from a separate Railway service/container (`ripple-smoke-runner`) pinned to the **same source commit** as the canonical server. It called the public HTTPS domain of `ripple-v12`; it did not call the MCP server in-process or over localhost.

The canonical server and the independent runner were both pinned to:

```text
708f9861b48745ca6d04d67df0e7efa2d329c25e
```

That same commit also passed the public GitHub Actions quality gate.

## Public CI corroboration

GitHub Actions run `33850775269` completed successfully on the tested commit and reported:

```text
43 passed
12 passed in tests/test_mcp_protocol_2025_11_25.py
6/6 adversarial scenarios PASS
Release Gate: PASS
committed evidence drift: 0
```

## Verified remote flow

The independent Railway runner exercised the authenticated public flow:

1. `GET /healthz` → 200
2. `GET /readyz` → 200
3. `GET /.well-known/oauth-protected-resource` → 200
4. `GET /.well-known/oauth-authorization-server` → 200
5. OAuth client-credentials token → 200
6. OAuth authorization-code + PKCE S256 approval → redirect success
7. OAuth user token exchange → 200
8. MCP `initialize` → 200, protocol `2025-11-25`
9. MCP `notifications/initialized` → accepted
10. MCP `tools/list` → 200
11. `record_change` → 200
12. `preview_repair_plan` → 200
13. `approve_repair_plan` → 200
14. `execute_repair_plan` → 200
15. exact replay `execute_repair_plan` → 200
16. MCP session termination → success

## Fresh semantic assertions

The pinned independent runner printed exactly:

```text
base: https://ripple-v12-production.up.railway.app
protocol: 2025-11-25
tools: record_change, preview_repair_plan, approve_repair_plan, execute_repair_plan, get_repair_status
change: 2026-09-11T18:00:00
preview: 5 impacts / 0 writes
approval writes: 0
execute: 5 receipts / 5 unique writes
replay: 5 deduplicated / 5 unique writes
Ripple authenticated MCP smoke: PASS
```

Therefore the public deployment verifies the core invariant:

> interpret → preview with zero writes → exact approval with zero writes → bounded execution → authoritative receipts → replay without duplicate external writes.

## Post-smoke state

After the fresh PASS:

- the canonical server was redeployed successfully on the same tested source commit;
- `/readyz` remained healthy;
- the smoke runner was retired with restart policy `NEVER` and a one-shot retirement command;
- no credentials, access tokens, passwords or client secrets are stored in this report or repository evidence.

## Disclosure

The five downstream service adapters remain deterministic simulated integrations for the hackathon MVP. The MCP Streamable HTTP transport, OAuth surfaces, public HTTPS deployment, exact approval boundary, execution ledger, receipts, replay behavior, CI validation and independent remote smoke described above are real running software.

No live AWS Bedrock invocation, Alexa+ production client, real airline/ride/reservation/delivery/care provider, or real payment integration is claimed.
