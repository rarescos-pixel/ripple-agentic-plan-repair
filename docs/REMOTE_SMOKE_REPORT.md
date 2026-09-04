# Ripple — Remote Authenticated MCP Smoke Report

**Status: PASS**

- Date: 2026-09-04
- Public endpoint: `https://ripple-v12-production.up.railway.app`
- MCP endpoint: `https://ripple-v12-production.up.railway.app/mcp`
- Protocol version: `2025-11-25`
- Server deployment: Railway `a3f66daa-7625-490f-9d0a-fefa3ee86a6a` — `SUCCESS`
- Smoke-runner deployment: Railway `c015ec16-cd2e-425e-882c-7b6dc669dfd9` — `SUCCESS`
- Source commit tested: `e4097ed8e6a4c6f42b75abec5ec6ae51bf836097`

## Independent execution topology

The smoke test ran from a separate Railway service/container (`ripple-smoke-runner`) and called the public HTTPS domain of `ripple-v12`. It did not call the MCP server in-process or over localhost.

## Verified flow

1. `GET /healthz` → 200
2. `GET /readyz` → 200
3. `GET /.well-known/oauth-protected-resource` → 200
4. `GET /.well-known/oauth-authorization-server` → 200
5. OAuth client-credentials token → 200
6. OAuth authorization-code + PKCE S256 approval → 303
7. OAuth user token exchange → 200
8. MCP `initialize` → 200, protocol `2025-11-25`
9. MCP `notifications/initialized` → 202
10. MCP `tools/list` → 200
11. `record_change` → 200
12. `preview_repair_plan` → 200
13. `approve_repair_plan` → 200
14. `execute_repair_plan` → 200
15. exact replay `execute_repair_plan` → 200
16. MCP session `DELETE /mcp` → 204

## Semantic assertions

The independent runner printed:

```text
Ripple authenticated MCP smoke: PASS
protocol: 2025-11-25
tools: record_change, preview_repair_plan, approve_repair_plan, execute_repair_plan, get_repair_status
change: 2026-09-11T18:00:00
preview: 5 impacts / 0 writes
approval writes: 0
execute: 5 receipts / 5 unique writes
replay: 5 deduplicated / 5 unique writes
```

Therefore the public deployment verifies the core invariant:

> interpret → preview with zero writes → exact approval with zero writes → bounded execution → authoritative receipts → replay without duplicate external writes.

## Server-side corroboration

Railway HTTP/runtime logs for the target server independently record the same public flow from an external source IP and `python-httpx/0.28.1`, including OAuth endpoints, MCP POSTs and the final 204 session deletion. Observed proxy durations for individual smoke requests were approximately 1–8 ms inside Railway's recorded request path. These timings are evidence for this deployment only and are not claimed as general Internet latency.

## Disclosure

The five downstream service adapters remain deterministic simulated integrations for the hackathon MVP. The MCP Streamable HTTP transport, OAuth surfaces, public HTTPS deployment, approval boundary, execution ledger and replay behavior tested above are real running software.

No credentials, access tokens, passwords or client secrets are stored in this report.
