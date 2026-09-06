# Ripple — MASTER competition state

## Competition targets — LOCKED

- **Primary Track:** Alexa+
- **Mini Challenge:** AWS Builder — canonical public runtime is AWS ECS Express Mode / Fargate with structural Bedrock + DynamoDB + CloudWatch
- **Mini Challenge:** Open Source — new MIT-licensed Ripple repository created during the hackathon window

Entering Open Source adds no product feature and does not alter the Alexa+ architecture. Required fields/evidence are in `docs/OPEN_SOURCE_SUBMISSION.md`.

## Product lock

**Tell Alexa one thing that changed. Ripple fixes what breaks downstream.**

Ripple is a **money-aware consequence-repair layer for Alexa+**. It represents commitments as a dependency graph, propagates a changed fact to downstream impacts, quantifies direct economic exposure, selects the safe repair that preserves the most net value, asks for one exact approval, then performs bounded idempotent execution with authoritative receipts.

Do not reopen product discovery unless a near-identical competitor destroys differentiation, the rules make Ripple ineligible, or a material blocker destroys the demo.

## Safety invariant — LOCKED

**LLM proposes → deterministic policy validates → user approves exact plan → bounded/idempotent tools execute → receipts are authoritative.**

The LLM may normalize language. It may not choose the money-spending repair, bypass deterministic policy, approve, or execute provider writes.

## Golden contract — VERIFIED

1. Golden cascade detects exactly **5 impacts**.
2. Financial summary: **$116 direct avoidable loss, $42 repair cost, $74 net direct cash preserved**.
3. Exactly **5** bounded external actions.
4. Preview and approval perform **0 writes**.
5. Approval binds to plan ID, version, exact content/snapshot, maximum cost and notification scope.
6. Material drift forces re-approval.
7. Ambiguous provider state blocks before the first write.
8. Replay and interrupted recovery produce **0 duplicate external writes**.
9. Provider failure remains truthful/partial.
10. Missed deadlines remain unresolved rather than fabricated as saved.
11. Hard user constraints filter options before economic optimization.
12. Repair selection maximizes **avoidable loss − repair cost** with deterministic tie-breakers.
13. Exact approved proposals can be recovered across MCP process/session restart only by the same owner subject and exact snapshot.

Deterministic release/adversarial gate: **PASS**. Canonical generated evidence: `docs/VALIDATION_REPORT.md`, `docs/EVIDENCE_MATRIX.md`, `docs/ADVERSARIAL_FAILURE_MATRIX.md`.

## Generality contract — VERIFIED

Event Operations scenario:

- 5 impacts across AV, catering, VIP transport, security and sponsor briefing;
- **$5,800** avoidable loss;
- **$620** repair cost;
- **$5,180** net direct cash preserved;
- cheaper-but-lower-value alternative intentionally rejected.

## Real-provider contract — VERIFIED

At least one external provider path is real rather than simulated. The bounded GitHub Issues adapter is repository/issue allowlisted, reversible, zero-cost and runs through Ripple's exact approval + Executor + receipt boundary.

Live proof: external write PASS; provider readback PASS; exact replay deduplicated PASS; exact restore PASS; provider cost $0.

## Public Alexa+ / MCP — VERIFIED SOFTWARE-SIDE

- Base: `https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws`
- MCP: `https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws/mcp`
- Protocol: `2025-11-25` Streamable HTTP.
- OAuth discovery + client credentials + authorization-code/PKCE S256 + refresh flow.
- Alexa-compatible refresh can omit `resource`; explicitly wrong resource remains rejected.
- Five tools: `record_change`, `preview_repair_plan`, `approve_repair_plan`, `execute_repair_plan`, `get_repair_status`.
- Money-first Repair Card is a real display-only MCP App resource.
- Alexa+ package points to the canonical AWS MCP endpoint and AWS-hosted 600×900 carousel asset.
- The documented Alexa Local Inspector JSON-only `Accept` request shape is regression-tested.

No actual Alexa+ production-client session is claimed unless actually exercised. The rules-permitted simulated Alexa+ experience remains a valid demo path backed by the real MCP runtime.

## AWS boundary — CANONICAL PUBLIC RUNTIME LIVE

**AWS services are live and structurally verified. The canonical public runtime is AWS-backed.**

Locked AWS architecture:

- **Amazon ECS Express Mode / Fargate** — canonical public MCP compute and HTTPS ingress;
- **Amazon Bedrock / Nova 2 Lite** — constrained changed-fact normalization only;
- **Amazon DynamoDB** — durable proposal/approval/idempotency/authoritative receipts;
- **Amazon CloudWatch Logs** — redacted structured traces;
- **IAM task roles + GitHub OIDC** — runtime and deployment identity without static application AWS keys;
- **AWS Budgets / anomaly controls** — cost guardrails.

### Exact-SHA canonical release invariant

A technical release is canonical only when one source SHA satisfies all of these:

1. exact SHA is built and pushed to ECR;
2. immutable digest is placed in the Fargate task definition;
3. ECS Express converges to that task definition;
4. infrastructure-role trust is restored in place and RoleId is preserved;
5. public `/readyz` repeatedly reports `aws-structural`, DynamoDB + Bedrock + CloudWatch and the exact source SHA;
6. authenticated OAuth + MCP smoke passes;
7. fresh-session replay is `5/5 deduplicated` and authoritative unique writes stay `5 → 5`, proving **0 new provider writes**;
8. CloudWatch contains runtime trace evidence;
9. ECR digest readback matches;
10. temporary bootstrap cutover permission is removed after successful proof.

Earlier Railway-hosted evidence remains historical audit evidence only. Railway is no longer the canonical architecture.

## Cost / failure proof — VERIFIED

- Judge-verifiable deterministic cost benchmark: `docs/COST_BENCHMARK_2026-09-06.md`.
- Failure-truth matrix: `docs/ADVERSARIAL_FAILURE_MATRIX.md`.
- Canonical AWS compute is intentionally one bounded task rather than duplicated application tiers.
- Economic decision policy remains deterministic and separate from infrastructure cost claims.

## Open Source boundary — ELIGIBLE / SUBMISSION-READY

Repository created **2026-09-04**, inside the submission window that began **2026-08-31**, public and MIT licensed.

- project repo: `https://github.com/rarescos-pixel/ripple-agentic-plan-repair`
- GitHub user: `rarescos-pixel`
- representative contribution: `https://github.com/rarescos-pixel/ripple-agentic-plan-repair/pull/22`
- what/how/why: `docs/OPEN_SOURCE_SUBMISSION.md`

## Current limitations — explicit

- airline, ride, reservation, delivery, pet-care and calendar provider adapters remain deterministic simulators;
- one bounded GitHub Issues external-provider path is real and independently live-proven;
- example dollar values are deterministic fixtures, not market statistics;
- no actual Alexa+ production-client session is claimed unless official onboarding/inspection is exercised;
- the embedded OAuth server is a hackathon/demo identity surface, not a production identity provider.

## Submission lock

Judge-facing materials lead with customer value:

> **One thing changed → five commitments broke → $116 is at risk → repair for $42 → preserve $74 → approve?**

Product promise: **repair the cascade without opening five apps/sites.**

Do not lead with protocol details, hashes, logs or AWS diagrams.

Required close sequence:

1. keep core / exact-approval / recovery / real-provider / adversarial / cost evidence green;
2. complete one exact-SHA AWS canonical release proof and freeze that SHA;
3. keep Alexa add-on endpoint/media aligned with the exact public AWS runtime;
4. keep friction log / product feedback / README / submission evidence coherent;
5. official Alexa+ Inspector/onboarding if accessible, as bonus rather than blocker;
6. monitor official Alexa+/Devpost updates until submission freeze;
7. **STOP before video and work on video only with Rareș explicitly present**;
8. final judge-first video under 3 minutes;
9. Devpost submission and adversarial final audit;
10. technical freeze through judging.
