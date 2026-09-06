# Judge Runbook — fastest path to Ripple evidence

The repository is designed so Ripple can be understood without running anything, while every important claim still has executable or independently observed evidence.

## 20 seconds — understand the product

> **One thing changed → 5 commitments affected → $116 at risk → repair for $42 → preserve $74 → approve?**

Ripple is a **money-aware consequence-repair layer for Alexa+**. It is not a generic Q&A/API wrapper: it finds a downstream cascade, prices the consequence set, chooses the safe repair that preserves the most net value, binds authority to one exact plan and proves effects with receipts.

## 60 seconds — inspect the public proof

Public MCP:

`https://ripple-v12-production.up.railway.app/mcp`

Verified remote contract:

```text
protocol: 2025-11-25
preview: 5 impacts / 0 writes
approval writes: 0
execute: 5 receipts / 5 unique writes
replay: 5 deduplicated / still 5 unique writes
```

Current exact-revision evidence:

- source SHA deployed/proven: `58898530b40564e1b0025db4ac8ea7d2f9249817`;
- Railway deployment: SUCCESS;
- independent `Ripple Railway production proof`: SUCCESS.

If the repository advances beyond that SHA before freeze, the exact-revision proof must be repeated for the final head.

See:

- `docs/ALEXA_REMOTE_EVIDENCE.md`
- `docs/REMOTE_SMOKE_REPORT.md`
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

## AWS Builder — direct structural evidence is LIVE

A completed AWS evidence workflow independently exercises:

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
- real DynamoDB authoritative receipt write/readback and conditional replay rejection;
- real CloudWatch Logs structured event write + readback;
- temporary GitHub OIDC credentials rather than committed static AWS keys.

See `docs/AWS_DIRECT_LIVE_EVIDENCE.md`.

Claim boundary:

> **AWS services are live and structurally verified; the canonical public Railway AWS-runtime cutover is pending.**

Do not interpret the direct live proof as a claim that every current public Railway request already uses AWS. That stronger cutover remains deliberately gated by a credential-safe external-workload identity/transfer path.

## Cost / failure evidence

- `docs/COST_BENCHMARK_2026-09-06.md` — deterministic judge-verifiable cost model/benchmark;
- `docs/ADVERSARIAL_FAILURE_MATRIX.md` — failure truth, drift, interruption and recovery proof;
- AWS architecture remains pay-per-use with no always-on AWS compute added merely for a larger diagram.

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
- no actual Alexa+ production-client session is claimed without evidence;
- direct AWS services are live-proven, while the public Railway AWS-backend cutover is still pending.

## VIDEO

The video phase is intentionally outside this runbook's current execution scope. **Do not change video materials until Rareș explicitly unlocks that phase.**
