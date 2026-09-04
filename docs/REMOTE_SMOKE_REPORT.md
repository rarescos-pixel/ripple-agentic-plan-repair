# Ripple — Remote Authenticated MCP Smoke Report

**Status: PASS**

- Date: 2026-09-04
- Public endpoint: `https://ripple-v12-production.up.railway.app`
- MCP endpoint: `https://ripple-v12-production.up.railway.app/mcp`
- Protocol version: `2025-11-25`
- Source commit tested: `52bf87d245802e91b4c59aad1a369a285af87a4f`
- GitHub Actions quality gate: run `33875453562` — `SUCCESS`
- Canonical v1.5 server deployment used by smoke: Railway `571e1585-8218-4183-8e05-c622a989f608` — `SUCCESS`
- Independent smoke-runner deployment: Railway `3ad074ae-3183-4b2d-bb2e-607ec429423d` — `SUCCESS`
- Post-smoke credential-rotation server deployment: Railway `98fa445c-bd5b-4793-ab64-7f923896aeba` — `SUCCESS`
- Runner retirement deployment: Railway `c014af33-8a21-4eeb-b2e2-43695f43b206` — `SUCCESS`

## Independent execution topology

The smoke test ran from a separate Railway service/container (`ripple-smoke-runner`) pinned to the **same source commit** as the canonical server. It called the public HTTPS domain of `ripple-v12`; it did not call the MCP server in-process or over localhost.

Both the target server and independent runner were pinned to:

```text
52bf87d245802e91b4c59aad1a369a285af87a4f
```

That exact commit passed the independent pull-request quality gate before fast-forward promotion to `main`.

## Public CI corroboration

GitHub Actions run `33875453562` completed successfully and reported:

```text
64 passed
12 passed in tests/test_mcp_protocol_2025_11_25.py
cfn-lint infra/ripple-aws.json: PASS
7/7 executable/adversarial scenarios PASS
Release Gate v1.5: PASS
AWS Ready Gate v1.5: PASS
committed evidence drift: 0
```

The AWS-ready gate verifies DynamoDB on-demand/PITR configuration, a tagged Bedrock Application Inference Profile, bounded CloudWatch retention, a project-tag budget, constrained runtime IAM resources, inference-profile conditions, and five normalization benchmark fixtures. It is configuration/contract evidence only, not evidence of live AWS calls.

## Verified remote flow

The independent Railway runner exercised the authenticated public flow with all AWS runtime switches absent/off:

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

Therefore the public v1.5 deployment preserves the core runtime invariant:

> interpret → preview with zero writes → exact approval with zero writes → bounded execution → authoritative receipts → replay without duplicate external writes.

## v1.5 AWS-ready additions corroborated by CI

The same tested source commit includes:

- deployable CloudFormation for DynamoDB, CloudWatch Logs, a Bedrock Application Inference Profile, IAM and AWS Budget;
- DynamoDB `PAY_PER_REQUEST`, encryption and seven-day point-in-time recovery;
- a tagged Bedrock Application Inference Profile for Ripple cost attribution;
- an IAM managed policy limited to Ripple state, one trace stream and Bedrock invocation through the Ripple inference profile;
- a 14-day CloudWatch retention policy and `ripple.trace.v1` secret-redacted trace sink;
- opt-in runtime switches for Bedrock normalization and CloudWatch tracing;
- a live-capable five-case Nova Lite vs Nova 2 Lite benchmark with quality-first selection policy;
- deployment and teardown scripts;
- a project-tag-scoped default $10 monthly budget with 50%, 80% and 100% actual-spend email thresholds;
- `cfn-lint` as a mandatory CI gate.

The deployable Railway image now contains the AWS SDK, but the canonical public service used for this smoke had no AWS runtime switch variables enabled. The default verified path therefore remained the deterministic non-AWS path.

## Post-smoke state

After the fresh PASS:

- the canonical server credentials were rotated internally without exposing credential values;
- the canonical service redeployed successfully on the same tested source commit;
- the smoke runner was retired with restart policy `NEVER` and sleeping enabled;
- no credentials, access tokens, passwords or client secrets are stored in this report or repository evidence.

## Disclosure

The five downstream service adapters remain deterministic simulated integrations for the hackathon MVP. MCP Streamable HTTP, OAuth surfaces, public HTTPS deployment, exact approval boundary, Repair Card structured output, execution receipts, replay behavior, CI validation and the independent v1.5 remote smoke are real running software.

Ripple v1.5 is **AWS-ready verified**, not **AWS-live verified**. The CloudFormation template, Bedrock adapter/benchmark harness, DynamoDB adapter, CloudWatch trace sink, IAM policy and Budget configuration are real code and pass local/CI validation, but no AWS stack, live Bedrock invocation, live DynamoDB table, live CloudWatch trace, active tag-filtered AWS Budget, Alexa+ production client, real airline/ride/reservation/delivery/care provider, or real payment integration is claimed yet.
