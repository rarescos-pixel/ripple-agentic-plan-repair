# Ripple — MASTER competition state

## Competition targets — LOCKED

- **Primary Track:** Alexa+
- **Mini Challenge:** AWS Builder, only after structural AWS LIVE evidence passes
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

Deterministic release/adversarial gate: **PASS**. Canonical generated evidence: `docs/VALIDATION_REPORT.md` and `docs/EVIDENCE_MATRIX.md`.

## Generality contract — VERIFIED

Consumer travel is the demo wedge, not the architecture.

Event Operations scenario:

- 5 impacts across AV, catering, VIP transport, security and sponsor briefing;
- **$5,800** avoidable loss;
- **$620** repair cost;
- **$5,180** net direct cash preserved;
- cheaper-but-lower-value alternative intentionally rejected.

## Public Alexa+ / MCP — VERIFIED SOFTWARE-SIDE

- Base: `https://ripple-v12-production.up.railway.app`
- MCP: `https://ripple-v12-production.up.railway.app/mcp`
- Protocol: `2025-11-25` Streamable HTTP.
- OAuth discovery + client credentials + authorization-code/PKCE S256 + refresh flow.
- Alexa-compatible refresh can omit `resource`; explicitly wrong resource remains rejected.
- Five tools: `record_change`, `preview_repair_plan`, `approve_repair_plan`, `execute_repair_plan`, `get_repair_status`.
- Independent remote MCP runner: PASS.
- Remote semantics: 5 impacts → 0 preview writes → 0 approval writes → 5 receipts / 5 unique writes → replay 5/5 deduplicated.
- Money-first Repair Card is a real display-only MCP App resource.
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
- monitor Alexa+/SDK/API updates during the hackathon, but adopt only changes with concrete score gain and low regression risk;
- request the official $150 AWS promotional credits if not already requested.

## AWS boundary — AWS-READY, NOT AWS-LIVE VERIFIED

Railway remains the public MCP host. No ECS/Fargate migration is allowed without a concrete economic/technical reason.

Structural AWS roles:

- **Amazon Bedrock** — constrained changed-fact normalization only;
- **Amazon DynamoDB** — durable approval/idempotency/authoritative receipts;
- **Amazon CloudWatch Logs** — redacted structured traces;
- **IAM** — least-privilege runtime policy;
- **AWS Budgets** — cost guardrails;
- **CloudFormation** — reproducible stack.

Implemented and CI-validated:

- IaC and cfn-lint;
- live Nova Lite vs Nova 2 Lite benchmark harness with quality-first selection;
- live resource verifier;
- Railway runtime switches and fail-closed structural-AWS requirement;
- external-runtime least-privilege credential lifecycle, idempotent reuse and resilient teardown;
- post-cutover AWS runtime smoke/restart/replay assertions.

Do not claim AWS LIVE until one real source SHA proves Bedrock + DynamoDB + CloudWatch + Budget/IAM and the public Railway service passes fresh-session replay with zero duplicate provider writes.

Do **not** add AgentCore, Strands or Kiro only to make the AWS Builder diagram larger. Finish the existing structural multi-service AWS path first.

## Open Source boundary — ELIGIBLE / SUBMISSION-READY

The repository was created on **2026-09-04**, inside the submission window that began **2026-08-31**, and is public with an MIT license.

Open Source submission packet:

- project repo: `https://github.com/rarescos-pixel/ripple-agentic-plan-repair`
- GitHub user: `rarescos-pixel`
- representative contribution URL: `https://github.com/rarescos-pixel/ripple-agentic-plan-repair/pull/22`
- required what/how/why text: `docs/OPEN_SOURCE_SUBMISSION.md`

No separate feature work is required merely to qualify. Any further open-source work must have independent engineering/judging value.

## Current limitations — explicit

- airline, ride, reservation, delivery, pet-care and calendar provider adapters are deterministic simulators;
- example dollar values are deterministic scenario fixtures, not market statistics;
- no actual Alexa+ production-client session is claimed unless official onboarding/inspection is exercised;
- official Alexa+ production-client access is **not** a submission prerequisite; the simulated Alexa+ path is explicitly permitted;
- the current public Railway service has not yet been claimed as structurally AWS-backed;
- the embedded OAuth server is a hackathon/demo identity surface, not a production identity provider.

## Submission lock

Judge-facing materials must lead with customer value:

> **One thing changed → five commitments broke → $116 is at risk → repair for $42 → preserve $74 → approve?**

The implied product promise is: **repair the cascade without opening five apps/sites.**

Do not lead with protocol details, dependency graphs, hashes, logs or AWS diagrams.

Required submission-close sequence after Sep 3 session intelligence:

1. judge-facing simulated Alexa+ conversation + Repair Card polish, backed by the real public MCP;
2. request/confirm the official $150 AWS promotional credits if not already done;
3. AWS LIVE evidence and Railway structural cutover;
4. friction log / product feedback final coherence and evidence freeze;
5. official Alexa+ Inspector/onboarding **if accessible**, as bonus evidence rather than a blocker;
6. monitor official Alexa+/Devpost updates until submission freeze;
7. final judge-first video under 3 minutes;
8. Devpost submission and adversarial final audit;
9. technical freeze through judging.
