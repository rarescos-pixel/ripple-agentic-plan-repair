# Ripple

**v1.2 — Alexa+ remote MCP milestone**

**Tell Alexa one thing that changed. Ripple fixes what breaks downstream.**

Ripple is a consequence-aware plan repair agent for the Amazon Developer Hackathon. One changed fact is propagated through a dependency graph into a bounded repair plan across heterogeneous commitments.

## Live deployment

- Public HTTPS base: `https://ripple-v12-production.up.railway.app`
- MCP endpoint: `https://ripple-v12-production.up.railway.app/mcp`
- Protocol: `2025-11-25` Streamable HTTP
- Railway deployment: **SUCCESS**
- Independent remote authenticated smoke: **PASS**

The remote smoke ran from a separate Railway container and exercised OAuth discovery, client credentials, authorization-code + PKCE S256, MCP initialization, tool discovery, change recording, preview, exact approval, execution, replay and session deletion against the public HTTPS endpoint. See `docs/REMOTE_SMOKE_REPORT.md`.

## Verified behavior

Remote gate result:

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

The core invariant is therefore verified over public HTTPS:

**interpret → deterministic validation → zero-write preview → exact approval → bounded idempotent execution → authoritative receipts → duplicate-free replay.**

## Current milestone

The MVP includes deterministic dependency predicates, exact-content approval, provider-ambiguity preflight, hard preference constraints, truthful unresolved/failure states, idempotent replay, interruption recovery, a constrained Bedrock adapter boundary, a simulated Alexa+ web experience, a real MCP Streamable HTTP server, OAuth discovery/authentication surfaces, container deployment assets, and a public Railway runtime.

No live AWS Bedrock invocation, Alexa+ production client, or real airline/ride/reservation/delivery/care/payment provider integration is claimed. The five downstream service adapters remain deterministic simulated integrations. The public MCP transport, OAuth surfaces, approval boundary, execution ledger, receipts and replay behavior are real running software.

## Local validation baseline

The v1.2 local freeze previously passed:

```text
43/43 tests PASS
12/12 MCP + OAuth protocol tests PASS
6/6 adversarial scenarios PASS
release gate PASS
```

## MCP server

Run locally:

```bash
PYTHONPATH=src python -m ripple.mcp_server
```

Local endpoint: `http://127.0.0.1:8000/mcp`.

The server implements stateful Streamable HTTP initialization, `MCP-Session-Id`, `tools/list`, `tools/call`, Origin validation, protocol-version enforcement, OAuth scope separation, exact approval and replay-safe execution.

## MCP tools

- `record_change`
- `preview_repair_plan`
- `approve_repair_plan`
- `execute_repair_plan`
- `get_repair_status`

## Golden scenario

User says:

> “Our flight home was cancelled. We'll land tomorrow at 18:00.”

Ripple identifies five downstream commitments and produces the golden contract:

- 5 impacts
- $42 added recovery cost
- $116 direct avoidable loss
- $74 net direct cash preserved
- 0 writes before approval
- 0 writes during approval
- 5 execution receipts
- exact replay produces 5 deduplications and still only 5 unique writes

## Authentication model

Ripple v1.2 exposes:

- `/.well-known/oauth-protected-resource`
- `/.well-known/oauth-authorization-server`
- OAuth client-credentials for `mcp:service`
- OAuth authorization-code + PKCE S256 for `mcp:tools`
- refresh-token issuance for the demo-user flow
- scope separation: service tokens may initialize/list tools but may not execute user tools

The embedded OAuth server is a hackathon/demo implementation, not a production identity provider.

## Safety fixes

- Web/MCP approval validates the exact snapshot presented to the user; the server does not silently regenerate approval against mutable state.
- The deterministic demo interpreter parses the actual HH:MM stated by the user. `18:00` and `23:55` create different canonical changes and plan snapshots.
- Approval hashing includes judge-visible impact content, actions, totals and scope.
- Provider ambiguity, stale approval, changed cost/scope and replay are handled fail-closed or truthfully unresolved.

## Repository evidence

- `docs/REMOTE_SMOKE_REPORT.md` — independent public HTTPS MCP/OAuth evidence
- `scripts/mcp_smoke.py` — reproducible authenticated remote smoke test
- `src/ripple/mcp_server.py` — MCP Streamable HTTP + OAuth server
- `src/ripple/engine.py` — dependency analysis
- `src/ripple/executor.py` — bounded/idempotent execution
- `src/ripple/policy.py` — deterministic approval boundary
- `src/ripple/tools.py` — simulated service adapters

## AWS status

AWS integration remains a later milestone. A constrained Bedrock boundary was designed/tested locally, but the public runtime currently demonstrates Alexa+-eligible MCP integration without claiming a live Bedrock call.

## License

This project is intended to be submitted as an open-source hackathon project. The repository license and complete judge packet are finalized as part of the submission-readiness pass.
