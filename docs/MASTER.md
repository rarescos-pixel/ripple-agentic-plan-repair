# Ripple — MASTER competition state

## Competition targets — LOCKED

- **Primary Track:** Alexa+
- **Mini Challenge:** AWS Builder — direct structural AWS LIVE evidence is now verified; the stronger public Railway AWS-runtime cutover remains pending
- **Mini Challenge:** Open Source, using the new MIT-licensed Ripple repository created during the hackathon window

Entering Open Source adds no product feature and does not alter the Alexa+ architecture. Required fields/evidence are frozen in `docs/OPEN_SOURCE_SUBMISSION.md`.

## Product lock

**Tell Alexa one thing that changed. Ripple fixes what breaks downstream.**

Ripple is a **money-aware consequence-repair layer for Alexa+**. It represents commitments as a dependency graph, propagates a changed fact to downstream impacts, quantifies direct economic exposure, selects the safe repair that preserves the most net value, asks for one exact approval, then performs bounded idempotent execution with authoritative receipts.

Do not reopen product discovery unless a near-identical competitor destroys differentiation, the rules make Ripple ineligible, or a material blocker destroys the demo.

## Safety invariant — LOCKED

**LLM proposes → deterministic policy validates → user approves exact plan → bounded/idempotent tools execute → receipts are authoritative.**

The LLM may normalize language. It may not choose the money-spending repair, bypass deterministic policy, approve, or execute provider writes.

## Canonical entities

`PlanNode` / `DependencyEdge` / `ChangeEvent` / `Impact` / `RepairOption` / `RepairAction` / `RepairPlan` / `Approval` / `ExecutionReceipt`.

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
12. Intermediate fact nodes are traversed without invented actions.
13. Unaffected commitments are not repaired.
14. Repair selection maximizes **avoidable loss − repair cost** with deterministic tie-breakers.
15. Exact approved proposals can be recovered across MCP process/session restart only by the same owner subject and exact snapshot.

Deterministic release/adversarial gate: **PASS**. Canonical generated evidence: `docs/VALIDATION_REPORT.md`, `docs/EVIDENCE_MATRIX.md` and `docs/ADVERSARIAL_FAILURE_MATRIX.md`.

## Generality contract — VERIFIED

Consumer travel is the demo wedge, not the architecture.

Event Operations scenario:

- 5 impacts across AV, catering, VIP transport, security and sponsor briefing;
- **$5,800** avoidable loss;
- **$620** repair cost;
- **$5,180** net direct cash preserved;
- cheaper-but-lower-value alternative intentionally rejected.

## Real-provider contract — VERIFIED

At least one external provider path is real rather than simulated. The bounded GitHub Issues adapter is repository/issue allowlisted, reversible, zero-cost and runs through Ripple's existing exact approval + Executor + receipt boundary.

Live proof:

- external write: PASS;
- provider readback: PASS;
- exact replay deduplicated: PASS;
- exact restore through a second bounded approved plan: PASS;
- provider cost: $0.

This proves Ripple's execution contract against a real external API without pretending that airline/ride/reservation providers are already production integrations.

## Public Alexa+ / MCP — VERIFIED SOFTWARE-SIDE

- Base: `https://ripple-v12-production.up.railway.app`
- MCP: `https://ripple-v12-production.up.railway.app/mcp`
- Protocol: `2025-11-25` Streamable HTTP.
- OAuth discovery + client credentials + authorization-code/PKCE S256 + refresh flow.
- Alexa-compatible refresh can omit `resource`; explicitly wrong resource remains rejected.
- Five tools: `record_change`, `preview_repair_plan`, `approve_repair_plan`, `execute_repair_plan`, `get_repair_status`.
- Independent remote MCP runner: PASS on previously deployed verified revisions.
- Remote semantics: 5 impacts → 0 preview writes → 0 approval writes → 5 receipts / 5 unique writes → replay 5/5 deduplicated.
- Money-first Repair Card is a real display-only MCP App resource.
- Repair Card exposes deterministic “Why this plan?” evidence and execution receipt timeline without gaining approval/tool authority.
- Alexa+ package/media remote gate: PASS for 600×900 carousel, six icon dimensions, privacy/terms and canonical MCP endpoint.
- The documented Alexa Local Inspector JSON-only `Accept` request shape is regression-tested.

Evidence: `docs/ALEXA_REMOTE_EVIDENCE.md`, `docs/REMOTE_SMOKE_REPORT.md`, `docs/MCP_APP_EVIDENCE.md`.

## Sep 3 Amazon build-session intelligence — LOCKED STRATEGY UPDATE

Audit: `docs/SEPT3_BUILD_SESSION_AUDIT.md`.

The official rules plus the Sep 3 Amazon/Devpost build-session recap materially reduce the value of treating Alexa+ certification/onboarding as a blocker. Amazon explicitly permits a simulated Alexa+ experience, and the session recommends a web Alexa+ mockup connected to the real MCP server for the demo.

Therefore:

- public MCP is the authoritative runtime proof;
- the final demo must primarily show **customer → agent → rich Repair Card → exact approval → visible outcome**;
- use the phrase **repair the cascade without opening five apps/sites** to make the transactional value obvious;
- official Local Inspector/on-device evidence is bonus evidence if accessible, not a prerequisite;
- do not add a second approval path to the MCP App;
- monitor Alexa+/SDK/API updates during the hackathon, but adopt only changes with concrete score gain and low regression risk.

## AWS boundary — DIRECT LIVE VERIFIED / PUBLIC RUNTIME CUTOVER PENDING

Railway remains the public MCP transport host. No ECS/Fargate/Lambda migration is allowed without a concrete economic/technical reason.

Locked structural AWS roles:

- **Amazon Bedrock / Nova 2 Lite** — constrained changed-fact normalization only;
- **Amazon DynamoDB** — durable proposal/approval/idempotency/authoritative receipts;
- **Amazon CloudWatch Logs** — redacted structured traces;
- **IAM + GitHub OIDC** — bounded direct-evidence authority without committed static keys;
- **AWS Budgets / anomaly controls** — cost guardrails.

### VERIFIED direct AWS evidence

A completed AWS evidence workflow has proven:

- GitHub OIDC assume-role: PASS;
- DynamoDB live receipt write/readback: PASS;
- DynamoDB replay conditional-write rejection: PASS;
- real Nova 2 Lite inference: PASS;
- CloudWatch Logs structured event write + readback: PASS;
- aggregate `AWS_DIRECT_LIVE_EVIDENCE=PASS`.

Evidence: `docs/AWS_DIRECT_LIVE_EVIDENCE.md`.

### Stronger claim still pending

Do **not** yet say that the canonical public `ripple-v12` process is AWS-backed for every request. That requires the credential-safe Railway cutover to DynamoDB/Bedrock/CloudWatch and an exact-revision post-cutover public smoke/restart/replay proof.

Canonical wording until then:

> **AWS services are live and structurally verified; the canonical public Railway AWS-runtime cutover is pending.**

Do **not** add AgentCore, Strands, Kiro, Lambda, ECS or Fargate only to make the AWS Builder diagram larger.

## Cost / failure proof — VERIFIED

- Judge-verifiable deterministic cost benchmark exists in `docs/COST_BENCHMARK_2026-09-06.md`.
- Failure-truth matrix exists in `docs/ADVERSARIAL_FAILURE_MATRIX.md`.
- Architecture remains pay-per-use on AWS with no always-on AWS compute added for logo value.
- Economic decision policy remains deterministic and separate from infrastructure cost claims.

## Open Source boundary — ELIGIBLE / SUBMISSION-READY

The repository was created on **2026-09-04**, inside the submission window that began **2026-08-31**, and is public with an MIT license.

Open Source submission packet:

- project repo: `https://github.com/rarescos-pixel/ripple-agentic-plan-repair`
- GitHub user: `rarescos-pixel`
- representative contribution URL: `https://github.com/rarescos-pixel/ripple-agentic-plan-repair/pull/22`
- required what/how/why text: `docs/OPEN_SOURCE_SUBMISSION.md`

No separate feature work is required merely to qualify. Any further open-source work must have independent engineering/judging value.

## Current limitations — explicit

- airline, ride, reservation, delivery, pet-care and calendar provider adapters remain deterministic simulators;
- one bounded GitHub Issues external-provider path is real and independently live-proven;
- example dollar values are deterministic scenario fixtures, not market statistics;
- no actual Alexa+ production-client session is claimed unless official onboarding/inspection is exercised;
- official Alexa+ production-client access is **not** a submission prerequisite; the simulated Alexa+ path is explicitly permitted;
- the current public Railway service has not yet been claimed as AWS-backed for every request;
- the embedded OAuth server is a hackathon/demo identity surface, not a production identity provider.

## Submission lock

Judge-facing materials must lead with customer value:

> **One thing changed → five commitments broke → $116 is at risk → repair for $42 → preserve $74 → approve?**

The implied product promise is: **repair the cascade without opening five apps/sites.**

Do not lead with protocol details, dependency graphs, hashes, logs or AWS diagrams.

Required submission-close sequence:

1. keep core / exact-approval / recovery / real-provider / adversarial / cost evidence green;
2. complete credential-safe AWS-backed Railway cutover only if it can be done without weakening the canonical endpoint;
3. exact final Railway source SHA → independent public MCP smoke → fresh-session replay proof;
4. friction log / product feedback / README / submission evidence coherence and freeze;
5. official Alexa+ Inspector/onboarding **if accessible**, as bonus evidence rather than a blocker;
6. monitor official Alexa+/Devpost updates until submission freeze;
7. **STOP before video and work on video only with Rareș explicitly present**;
8. final judge-first video under 3 minutes;
9. Devpost submission and adversarial final audit;
10. technical freeze through judging.
