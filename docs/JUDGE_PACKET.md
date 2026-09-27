# Ripple — Judge Packet

Status: **winner-build technical evidence packet; VIDEO remains LOCKED.**

## The 10-second product

> **Tell Alexa one thing that changed. Ripple fixes what breaks downstream.**
>
> One changed arrival → **5 commitments affected → $116 at risk → $42 repair → $74 net preserved → approve?**

Ripple is a consequence-repair agent, not a Q&A wrapper. It discovers a dependency cascade, prices the consequence set, selects the safe repair that preserves the most net value, binds authority to one exact plan and proves every effect with receipts.

## The proof stack

| Judge question | Answer | Evidence |
|---|---|---|
| Does a real public agent exist? | **YES** | Canonical public MCP `2025-11-25` runtime on AWS ECS Express Mode / Fargate with exact-SHA release proof |
| Does it write before approval? | **NO** | Preview = 0 writes; approval = 0 writes |
| Is approval actually bounded? | **YES** | Plan ID/version/content hash + max cost + notification scope |
| Can it duplicate effects after replay/restart? | **NO in verified contract** | authoritative receipts, idempotency keys, restart recovery, replay 5/5 dedup |
| Does the model choose spending? | **NO** | deterministic economic planner/policy owns repair choice |
| Is the economic choice visible? | **YES** | Repair Card “Why this plan?” only when mechanically provable |
| Are all integrations fake? | **NO** | bounded real GitHub Issues provider: write/readback/dedup/restore PASS |
| Is AWS just a diagram? | **NO** | canonical ECS runtime + live Nova 2 Lite + DynamoDB receipt/replay + CloudWatch evidence |
| Is the public runtime AWS-backed? | **YES** | ECS task roles, exact-SHA readiness, authenticated MCP/OAuth smoke, Bedrock/DynamoDB/CloudWatch structural runtime |
| Is it travel-specific? | **NO** | Event Operations: $5,800 risk → $620 repair → $5,180 preserved |

## Public runtime

- Base: `https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws`
- MCP: `https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws/mcp`
- runtime mode: `aws-structural`
- canonical host: Amazon ECS Express Mode / Fargate
- release identity: exact Git SHA → immutable ECR digest → ECS task definition → repeated `/readyz` readback

Historical Railway deployment and smoke reports are retained only as audit evidence from the earlier hosting phase. They are not the current runtime and are not required for judging.

## Golden contract

```text
5 commitments affected
$116 direct avoidable loss
$42 repair cost
$74 net direct cash preserved
0 writes before approval
0 writes during approval
5 authoritative receipts
exact replay: 5/5 deduplicated
```

## Safety / recovery contract

```text
LLM proposes
→ deterministic policy validates
→ user approves exact plan
→ bounded/idempotent execution
→ authoritative receipts
```

Verified adversarial behaviors include material drift, ambiguous provider state, missed deadline truthfulness, hard preferences, provider failure, interruption and restart recovery without duplicate effects.

Evidence:
- `VALIDATION_REPORT.md`
- `ADVERSARIAL_FAILURE_MATRIX.md`
- `EVIDENCE_MATRIX.md`

## Real-provider proof

A deliberately narrow GitHub Issues provider demonstrates the external-write contract against a real API without pretending travel providers are production integrations.

```text
REAL_PROVIDER_WRITE=PASS
REAL_PROVIDER_READBACK=PASS
REAL_PROVIDER_REPLAY_DEDUP=PASS
REAL_PROVIDER_RESTORE=PASS
REAL_PROVIDER_COST_USD=0
REAL_PROVIDER_PROOF=PASS
```

The fixture is restored after the proof.

## AWS Builder proof

Canonical AWS evidence:

```text
AWS_OIDC=PASS
DYNAMODB_LIVE=PASS
DYNAMODB_RECEIPT_LIVE=PASS
AWS_REPLAY_DEDUP=PASS
BEDROCK_MODEL=eu.amazon.nova-2-lite-v1:0
BEDROCK_LIVE=PASS
CLOUDWATCH_LOGS_LIVE=PASS
AWS_DIRECT_LIVE_EVIDENCE=PASS
```

AWS role split:
- ECS Express Mode / Fargate: canonical public MCP compute and HTTPS ingress;
- Nova 2 Lite: constrained changed-fact normalization only;
- DynamoDB: durable proposal/approval/idempotency/receipts;
- CloudWatch Logs: redacted structured traces;
- ECS task roles: application runtime authority;
- GitHub OIDC: temporary bounded deployment/proof authority;
- Budgets/anomaly controls: bounded-spend guardrails.

Precise claim boundary:

> **Ripple's canonical public MCP runtime runs on AWS ECS Express Mode / Fargate with Bedrock, DynamoDB and CloudWatch structurally active.**

Every frozen release must bind that claim to the exact Git SHA, immutable image digest, task definition, public readiness, authenticated smoke and replay evidence.

## Design proof

The Repair Card is a real display-only MCP App. It shows:
- money at risk / repair cost / net preserved;
- affected commitments;
- exact approval CTA;
- deterministic economic rationale when provable;
- sanitized receipt timeline after execution.

It cannot approve or invoke execution tools.

Evidence: `MCP_APP_EVIDENCE.md`.

## Generality proof

Event Operations fixture:

```text
$5,800 avoidable loss
$620 repair cost
$5,180 net preserved
```

A cheaper candidate is rejected because it preserves less net value. The planner maximizes `avoidable loss − repair cost`, not “cheapest repair”.

## Cost / engineering discipline

- AWS pay-per-use;
- no unnecessary application tier duplicated for diagram value;
- budget/anomaly guardrails;
- judge-verifiable cost benchmark: `COST_BENCHMARK_2026-09-06.md`.

## What is intentionally not claimed

- airline/ride/reservation/delivery/pet-care/calendar production provider writes;
- market validity of fixture dollar values;
- official Alexa+ production-client session without evidence.

## Fast evidence order

1. README — understand product in seconds.
2. `JUDGE_RUNBOOK.md` — fastest reproduction route.
3. `AWS_READINESS.md` + `AWS_DIRECT_LIVE_EVIDENCE.md` — current public runtime and AWS proof.
4. `VALIDATION_REPORT.md` + `ADVERSARIAL_FAILURE_MATRIX.md` — safety/recovery.
5. real-provider workflow evidence — actual external write/readback/replay/restore.
6. `RUBRIC_MAP.md` — claim-to-criterion mapping.
7. `PRODUCT_FEEDBACK.md` / `FRICTION_LOG.md` — Amazon feedback bonus.

## Remaining before submission freeze

1. finish only score-positive non-video work;
2. require main Quality Gate PASS;
3. perform one exact-SHA AWS release proof on the final main SHA;
4. reconcile final public URL/SHA/evidence surfaces;
5. freeze repo/judge packet;
6. **STOP — VIDEO only with Rareș explicitly present**;
7. final Devpost copy/compliance audit.
