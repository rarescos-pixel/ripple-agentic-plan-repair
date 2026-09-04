# Ripple — Remote Authenticated MCP Smoke Report

**Status: PASS**

- Date: 2026-09-04
- Public endpoint: `https://ripple-v12-production.up.railway.app`
- MCP endpoint: `https://ripple-v12-production.up.railway.app/mcp`
- Protocol version: `2025-11-25`
- Source commit tested: `6c4da65525414dfc88d5a4210cdcf3a8604e0c96`
- GitHub Actions quality gate on that commit: run `33870882922` — `SUCCESS`
- Target server deployment used by the fresh smoke: Railway `f37b5714-08d0-414d-bab8-c65c7a550a3a` — `SUCCESS`
- Fresh smoke-runner deployment: Railway `533f7f26-b7d5-47f7-bed5-d89172b7b8ac` — `SUCCESS`
- Post-smoke credential-rotation server deployment: Railway `2f5a6f29-f7bf-4b9f-a577-b0fff3bb9021` — `SUCCESS`
- Runner retirement deployment: Railway `744e0e96-0d96-4d8c-869a-440472cf4c7f` — `SUCCESS`

## Independent execution topology

The fresh smoke test ran from a separate Railway service/container (`ripple-smoke-runner`) pinned to the **same source commit** as the canonical server. It called the public HTTPS domain of `ripple-v12`; it did not call the MCP server in-process or over localhost.

Both the target server and independent runner were on:

```text
6c4da65525414dfc88d5a4210cdcf3a8604e0c96
```

The same commit also passed the independent GitHub Actions quality gate before promotion to `main`.

## Public CI corroboration

GitHub Actions run `33870882922` completed successfully on the tested commit and reported:

```text
52 passed
12 passed in tests/test_mcp_protocol_2025_11_25.py
7/7 executable/adversarial scenarios PASS
Release Gate v1.4: PASS
committed evidence drift: 0
```

The protocol suite also asserts that `preview_repair_plan` returns the structured `ripple.repair-card.v1` money-first decision surface and that `approve_repair_plan` persists the exact approval while performing zero external writes.

## Verified remote flow

The independent Railway runner exercised the authenticated public flow:

1. public health/readiness and OAuth discovery;
2. OAuth service authentication;
3. OAuth authorization-code + PKCE user authentication;
4. MCP `initialize` using protocol `2025-11-25`;
5. MCP initialized notification and tool discovery;
6. `record_change`;
7. `preview_repair_plan`;
8. `approve_repair_plan`;
9. `execute_repair_plan`;
10. exact replay of `execute_repair_plan`;
11. session termination.

## Fresh semantic assertions

The pinned independent runner printed:

```text
Ripple authenticated MCP smoke: PASS
base: https://ripple-v12-production.up.railway.app
protocol: 2025-11-25
tools: record_change, preview_repair_plan, approve_repair_plan, execute_repair_plan, get_repair_status
change: 2026-09-11T18:00:00
preview: 5 impacts / 0 writes
approval writes: 0
execute: 5 receipts / 5 unique writes
replay: 5 deduplicated / 5 unique writes
```

Therefore the public deployment verifies the core runtime invariant:

> interpret → preview with zero writes → exact approval with zero writes → bounded execution → authoritative receipts → replay without duplicate external writes.

## v1.4 safety additions corroborated by CI

The same source commit additionally contains and tests:

- a money-first inline Repair Card: `$116 at risk → $42 repair → $74 net preserved`;
- exact approval persistence through the `StateStore` contract;
- a process-style SQLite restart test: two committed actions before restart, two deduplicated after restart, three new writes, five unique writes total;
- a DynamoDB state adapter for approvals and receipts;
- conditional DynamoDB publication so an authoritative `executed` receipt cannot be overwritten by a concurrent/later receipt;
- explicit disclosure that provider-level exactly-once still requires the downstream provider to honor Ripple's idempotency key or expose an equivalent transaction primitive.

## Post-smoke state

After the fresh PASS:

- the canonical server credentials were rotated again without storing credential values in repository evidence;
- the canonical service was redeployed successfully on the same source commit;
- the smoke runner was retired with restart policy `NEVER` and a one-shot retirement command;
- no credentials, access tokens, passwords or client secrets are stored in this report.

## Disclosure

The five downstream service adapters remain deterministic simulated integrations for the hackathon MVP. MCP Streamable HTTP, OAuth surfaces, public HTTPS deployment, exact approval boundary, Repair Card structured output, execution receipts, replay behavior, CI validation and independent remote smoke are real running software.

The restart-durable SQLite path and DynamoDB adapter are real executable code, but the canonical Railway deployment is not yet claiming a live DynamoDB table. No live AWS Bedrock invocation, Alexa+ production client, real airline/ride/reservation/delivery/care provider, or real payment integration is claimed yet.
