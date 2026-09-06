# AWS readiness — cost-efficient structural integration

## Decision
Use AWS only where it increases correctness and hackathon evidence. Railway remains the public MCP transport host; AWS strengthens the narrow capabilities where durable state, model normalization and trace evidence matter.

## Locked structural stack
1. **Amazon Bedrock / Nova 2 Lite** — one constrained inference per reported change; normalization only, never repair ranking or execution.
2. **DynamoDB** — durable proposal/approval state, idempotency ledger and authoritative receipts.
3. **CloudWatch Logs** — redacted structured traces for execution and recovery evidence.
4. **AWS Budgets / cost anomaly controls** — bounded-spend guardrails.

There is deliberately **no Lambda/ECS/Fargate duplication** in the locked architecture. The deterministic Ripple engine remains in the Railway-hosted MCP process. Adding another compute layer would increase cost and failure surface without improving the primary Alexa+ behavior.

## Cost controls
- on-demand Bedrock only;
- one bounded model call per change;
- temperature 0 and tightly bounded output;
- application-owned old state and allowlisted node/field context;
- DynamoDB on-demand;
- short CloudWatch retention and no raw prompt/secret logging;
- account-level budget/anomaly guardrails;
- no provisioned throughput or always-on AWS compute.

## Verified live boundary — 2026-09-06
Direct structural AWS evidence is now **PASS**:

- GitHub OIDC assume-role: PASS;
- DynamoDB table live: PASS;
- durable receipt write/readback: PASS;
- replay conditional-write rejection: PASS;
- Amazon Nova 2 Lite real inference: PASS;
- CloudWatch Logs structured event write + readback: PASS;
- aggregate marker: `AWS_DIRECT_LIVE_EVIDENCE=PASS`.

See [`AWS_DIRECT_LIVE_EVIDENCE.md`](AWS_DIRECT_LIVE_EVIDENCE.md) for the exact run and claim boundary.

## Remaining stronger runtime claim
The canonical public Railway service is **not yet claimed to be AWS-backed for every request**. That stronger statement requires a credential-safe Railway cutover plus an exact-revision public smoke proving Bedrock, DynamoDB and CloudWatch from the public MCP process.

Until that final cutover passes, use the precise wording:

> **AWS services are live and structurally verified; the canonical public Railway runtime cutover is pending.**

This is intentionally stricter than merely showing AWS resources or a successful SDK call.
