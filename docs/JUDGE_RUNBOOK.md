# Judge Runbook — fastest path to Ripple evidence

The repository is designed so Ripple can be understood without running anything, while every important claim still has executable or independently observed evidence.

## 20 seconds — understand the product

> **One thing changed → 5 commitments affected → $116 at risk → repair for $42 → preserve $74 → approve?**

Ripple is a **money-aware consequence-repair layer for Alexa+**. It is not a generic Q&A/API wrapper: it finds a downstream cascade, prices the consequence set, chooses the safe repair that preserves the most net value, binds authority to one exact plan and proves effects with receipts.

## 60 seconds — inspect the public proof

Canonical public MCP:

`https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws/mcp`

Canonical runtime:

- Amazon ECS Express Mode / Fargate;
- runtime mode `aws-structural`;
- Bedrock / Nova 2 Lite normalization;
- DynamoDB durable proposals, approvals, idempotency and receipts;
- CloudWatch redacted structured traces;
- IAM task roles for runtime authority;
- GitHub OIDC for bounded release/proof operations.

Verified remote contract:

```text
protocol: 2025-11-25
preview: 5 impacts / 0 writes
approval writes: 0
execute: 5 receipts / 5 authoritative unique writes
replay: 5/5 deduplicated / authoritative writes unchanged
```

A frozen release is accepted only when the exact Git SHA is bound to an immutable ECR digest and ECS task definition, `/readyz` repeatedly reports that exact revision, authenticated MCP/OAuth smoke passes, Bedrock is live, DynamoDB replay remains duplicate-free, CloudWatch contains execution evidence and the deployed digest reads back correctly.

Historical Railway reports remain available as evidence of the earlier hosting phase. They are not a current endpoint or a judging dependency.

See:

- `docs/AWS_READINESS.md`
- `docs/AWS_DIRECT_LIVE_EVIDENCE.md`
- `docs/ALEXA_REMOTE_EVIDENCE.md` — historical remote interoperability evidence
- `docs/REMOTE_SMOKE_REPORT.md` — historical independent remote smoke evidence
- `docs/MCP_APP_EVIDENCE.md`
- `docs/RELEASE_CHECKLIST.md`

## Safety / recovery — inspect what makes the agent trustworthy

The authority chain is:

**LLM proposes → deterministic policy validates → user approves exact plan → bounded/idempotent execution → authoritative receipts**

Verified properties:

- model never chooses the money-spending repair;
- 0 provider writes in preview and approval;
- exact approval binds plan ID/version/content hash, maximum cost and notification scope;
- material drift forces re-approval;
- ambiguous provider state fails closed;
- process/session restart can recover only the same persisted proposal for the same owner subject;
- partial execution resumes without duplicating already completed effects;
- replay produces authoritative deduplicated receipts rather than repeated writes.

See `docs/ADVERSARIAL_FAILURE_MATRIX.md` and `docs/VALIDATION_REPORT.md`.

## Real external provider — prove execution is not simulation-only

Ripple includes one deliberately narrow real provider adapter using GitHub Issues. The live proof runs through the existing exact approval and Executor boundary and then restores its fixture.

Verified live markers:

```text
REAL_PROVIDER_WRITE=PASS
REAL_PROVIDER_READBACK=PASS
REAL_PROVIDER_REPLAY_DEDUP=PASS
REAL_PROVIDER_RESTORE=PASS
REAL_PROVIDER_COST_USD=0
REAL_PROVIDER_PROOF=PASS
```

Travel-world airline/ride/reservation/delivery/pet-care/calendar providers remain deterministic simulations and are disclosed as such.

## Economic choice — understand why Ripple is different

Golden consumer fixture:

**$116 at risk → $42 repair → $74 net preserved.**

Event Operations generality fixture:

**$5,800 avoidable loss → $620 repair → $5,180 net preserved.**

The Event Operations scenario contains a cheaper repair that is intentionally rejected because it preserves less net value. Ripple ranks safe candidates by **avoidable loss − repair cost** with deterministic tie-breakers. The Repair Card emits “Why this plan?” evidence only when that comparison is mechanically provable from the immutable proposal.

## MCP App / Alexa+ surface

The Repair Card is a real display-only MCP App resource. It shows:

- affected commitments;
- at-risk dollars;
- repair cost;
- net preserved value;
- exact approval CTA;
- deterministic economic rationale when provable;
- post-execution receipt timeline and replay/dedup status.

The app cannot invoke approval or execution tools. Voice captures the changed fact; the visual surface makes money/scope and receipts easy to verify.

The hackathon rules permit a clearly labelled simulated Alexa+ experience backed by the real MCP server. No actual Alexa+ production-client session is claimed unless separately evidenced.

## AWS Builder — canonical runtime is LIVE

The current public runtime independently exercises:

```text
AWS_OIDC=PASS
DYNAMODB_RECEIPT_LIVE=PASS
AWS_REPLAY_DEDUP=PASS
BEDROCK_LIVE=PASS
CLOUDWATCH_LOGS_LIVE=PASS
AWS_DIRECT_LIVE_EVIDENCE=PASS
```

Meaning:

- real Amazon Nova 2 Lite inference;
- real DynamoDB durable receipt/replay behavior;
- real CloudWatch Logs structured trace evidence;
- ECS task roles rather than static application AWS keys;
- short-lived GitHub OIDC for release/proof authority.

See `docs/AWS_DIRECT_LIVE_EVIDENCE.md` and `docs/AWS_RUNTIME_CREDENTIALS.md`.

## Cost / failure evidence

- `docs/COST_BENCHMARK_2026-09-06.md` — deterministic judge-verifiable cost model/benchmark;
- `docs/ADVERSARIAL_FAILURE_MATRIX.md` — failure truth, drift, interruption and recovery proof.

## Run locally, if desired

```bash
python -m pip install -e . pytest
PYTHONPATH=src python -m pytest -q
```

For the MCP server:

```bash
PYTHONPATH=src python -m ripple.mcp_server
```

The canonical evidence files are faster to inspect than rebuilding the complete public environment from scratch.

## Truthfulness / limitations

See `docs/TECHNOLOGY_DISCLOSURE.md`, `docs/AWS_DIRECT_LIVE_EVIDENCE.md` and the README “What is real vs simulated” section.

- travel-world providers are deterministic fixtures;
- one bounded external-provider path is real and live-proven;
- fixture dollar amounts are scenario values, not market statistics;
- no actual Alexa+ production-client session is claimed without evidence.

## VIDEO

The video phase is intentionally outside this runbook's current execution scope. **Do not change video materials until Rareș explicitly unlocks that phase.**
