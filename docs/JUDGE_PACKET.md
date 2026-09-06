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
| Does a real public agent exist? | **YES** | Public MCP `2025-11-25` Streamable HTTP + exact-revision Railway proof |
| Does it write before approval? | **NO** | Preview = 0 writes; approval = 0 writes |
| Is approval actually bounded? | **YES** | Plan ID/version/content hash + max cost + notification scope |
| Can it duplicate effects after replay/restart? | **NO in verified contract** | authoritative receipts, idempotency keys, restart recovery, replay 5/5 dedup |
| Does the model choose spending? | **NO** | deterministic economic planner/policy owns repair choice |
| Is the economic choice visible? | **YES** | Repair Card “Why this plan?” only when mechanically provable |
| Are all integrations fake? | **NO** | bounded real GitHub Issues provider: write/readback/dedup/restore PASS |
| Is AWS just a diagram? | **NO** | real Nova 2 Lite + DynamoDB receipt/replay + CloudWatch write/readback PASS |
| Is the public Railway process already AWS-backed on every request? | **NOT CLAIMED** | credential-safe cutover still pending |
| Is it travel-specific? | **NO** | Event Operations: $5,800 risk → $620 repair → $5,180 preserved |

## Public runtime

- MCP: `https://ripple-v12-production.up.railway.app/mcp`
- exact-revision production SHA already proven during winner hardening: `58898530b40564e1b0025db4ac8ea7d2f9249817`
- deployment: PASS
- independent Railway production proof: PASS

Any merge after that SHA requires one final exact-revision deploy/proof before technical freeze.

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

Direct structural live evidence:

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
- Nova 2 Lite: constrained changed-fact normalization only;
- DynamoDB: durable proposal/approval/idempotency/receipts;
- CloudWatch Logs: redacted structured traces;
- GitHub OIDC: temporary bounded evidence-run authority;
- Budgets/anomaly controls: bounded-spend guardrails.

Precise claim boundary:

> **AWS services are live and structurally verified; the canonical public Railway AWS-runtime cutover is pending.**

Evidence: `AWS_DIRECT_LIVE_EVIDENCE.md`.

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

- AWS pay-per-use; no always-on AWS compute added for diagram value;
- no AgentCore/Step Functions/vector DB/multi-agent feature theatre without need;
- $5 budget guard + $5 anomaly threshold;
- judge-verifiable cost benchmark: `COST_BENCHMARK_2026-09-06.md`.

## What is intentionally not claimed

- airline/ride/reservation/delivery/pet-care/calendar production provider writes;
- market validity of fixture dollar values;
- official Alexa+ production-client session without evidence;
- AWS-backed execution for every public Railway request before credential-safe cutover.

## Fast evidence order

1. README — understand product in seconds.
2. `JUDGE_RUNBOOK.md` — fastest reproduction route.
3. `VALIDATION_REPORT.md` + `ADVERSARIAL_FAILURE_MATRIX.md` — safety/recovery.
4. real-provider workflow evidence — actual external write/readback/replay/restore.
5. `AWS_DIRECT_LIVE_EVIDENCE.md` — actual Bedrock/DynamoDB/CloudWatch proof.
6. `RUBRIC_MAP.md` — claim-to-criterion mapping.
7. `PRODUCT_FEEDBACK.md` / `FRICTION_LOG.md` — Amazon feedback bonus.

## Remaining before submission freeze

1. finish only score-positive non-video work;
2. make a bounded go/no-go decision on Railway AWS-runtime cutover;
3. merge the final technical/docs state;
4. repeat exact-revision Railway deployment + independent proof on the final SHA;
5. require main Quality Gate PASS;
6. freeze repo/judge packet;
7. **STOP — VIDEO only with Rareș explicitly present**;
8. final Devpost copy/compliance audit.
