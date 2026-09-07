# Amazon judging rubric mapping — 10/10 target state

Ripple is audited against the four equally weighted Stage 2 criteria. Claims are separated from observed evidence, simulated provider behavior is disclosed explicitly, and the canonical public architecture is AWS ECS Express Mode / Fargate.

## 1. Technical Implementation

**Target state: no-obvious-deduction / 10-of-10 candidate.**

Verified product evidence:

- public MCP `2025-11-25` Streamable HTTP endpoint;
- OAuth protected-resource / authorization-server discovery;
- service credentials plus authorization-code + PKCE S256 user flow and refresh path;
- five bounded MCP tools: record, preview, approve, execute, status;
- dependency traversal across heterogeneous commitments;
- deterministic net-value optimization;
- exact snapshot approval and zero-write preapproval phases;
- provider preflight, idempotency keys and authoritative receipts;
- exact approved-plan recovery across MCP process/session restart with owner binding and duplicate-free continuation;
- money-first Repair Card implemented as a real display-only MCP App resource;
- deterministic “Why this plan?” evidence plus post-execution receipt timeline;
- one bounded real external provider integration with live write → readback → replay dedup → exact restore at $0 provider cost;
- Alexa package/store-media and Local Inspector compatibility gates;
- adversarial/failure-truth matrix;
- canonical public AWS runtime on ECS Express Mode / Fargate with Bedrock, DynamoDB and CloudWatch;
- IAM task roles + GitHub OIDC, with no committed static application AWS credentials;
- CI validation for MCP protocol, Alexa request-shape compatibility, MCP App safety, package/media, AWS evidence/lifecycle, submission surfaces and generated-evidence drift.

**Freeze acceptance is stricter than source-level correctness.** Every frozen SHA must pass the full quality gate, an exact-SHA AWS public deployment proof, repeated exact-revision `/readyz` checks, authenticated MCP/OAuth smoke, fresh-session DynamoDB replay, and repeated public `/demo/api/evidence` = `7/7`.

Historical Railway evidence remains audit history only and does not define the current architecture.

## 2. Design

**Target state: no-obvious-deduction / 10-of-10 candidate once the final video is complete.**

Design contract:

- one utterance captures the changed fact;
- the first decision surface is money-first: affected commitments, dollars at risk, repair cost and net value preserved;
- voice summary, visual card, accessibility label and CTA disclose the same exact approval;
- Repair Card uses human-readable commitment names rather than technical IDs;
- “Why this plan?” is emitted only when the economic comparison is mechanically provable;
- execution returns a sanitized receipt timeline so new writes and replay dedup are visible;
- the MCP App is display-only: polish cannot bypass approval or execute tools;
- material drift forces re-approval;
- unresolved or expired work remains explicit;
- restart recovery preserves the exact already-approved authority rather than silently widening it.

The remaining design deliverable is presentation: the final sub-three-minute video must make the customer magic obvious before exposing protocol, cloud or release evidence.

## 3. Potential Impact

**Target state: no-obvious-deduction / 10-of-10 candidate with an external reality anchor in the judge-facing submission.**

Golden consumer fixture:

- **5** downstream commitments affected;
- **$116** direct avoidable loss;
- **$42** repair cost;
- **$74** net direct cash preserved.

Event Operations fixture:

- **$5,800** avoidable loss;
- **$620** repair cost;
- **$5,180** net direct cash preserved.

Why the impact claim is credible:

- Ripple prices the consequence set and repair rather than using generic productivity language;
- optimization maximizes net preserved value rather than merely minimizing repair cost;
- a cheaper-but-worse alternative is executable evidence in Event Operations;
- consumer travel is a narrow hero wedge while the dependency/economic engine is generic;
- dollar amounts are explicitly deterministic scenario fixtures, not market statistics;
- a bounded real provider proof demonstrates that the execution/receipt contract is not simulation-only;
- the final judge-facing copy should include one authoritative external disruption-volume anchor, explicitly separated from the fixture economics.

Applicable domains without changing the primitive include travel concierge, corporate travel, hospitality recovery, event operations, insurance workflows, executive assistance and other dependency-heavy operations.

## 4. Quality of the Idea

**Target state: no-obvious-deduction / 10-of-10 candidate.**

Ripple is not a basic MCP wrapper or single-turn information tool. Its primitive is **cascading consequence repair**:

> one real-world state change invalidates part of a dependency graph; Ripple identifies only the affected commitments, quantifies exposure, selects the safe repair that preserves the most value, obtains one exact approval and executes with durable receipts.

Differentiators that must remain visible:

1. dependency-aware consequence discovery rather than a fixed automation recipe;
2. deterministic economic choice rather than LLM-selected spending;
3. exact approval binding rather than generic “yes, proceed” authority;
4. recovery across interruption/restart without duplicate effects;
5. authoritative receipts and truthful partial/failure state;
6. voice-first Alexa+ input plus a rich visual MCP App decision surface.

Do not dilute this with feature-count competition, multi-agent theatre or decorative services.

## AWS Builder mini challenge

**Canonical public AWS runtime: LIVE / exact-SHA proof required per freeze.**

- ECS Express Mode / Fargate: canonical public HTTPS MCP runtime;
- Bedrock / Nova 2 Lite: constrained changed-fact normalization only;
- DynamoDB: durable state, exact approvals, idempotency and authoritative receipts;
- CloudWatch Logs: redacted structured execution traces;
- IAM task roles + GitHub OIDC: bounded runtime/deployment identity;
- Budgets / anomaly controls: spend guardrails.

The precise claim boundary is:

> **Ripple's canonical public MCP runtime runs on AWS ECS Express Mode / Fargate with Bedrock, DynamoDB and CloudWatch structurally active. Every frozen release must bind that claim to the exact Git SHA, immutable ECR digest, ECS task definition, public readiness, authenticated smoke and replay evidence.**

## Open Source mini challenge

**Eligible / submission-ready.**

Ripple is a new public MIT-licensed repository created during the hackathon window. The repository publishes the complete project plus reusable safety/interoperability patterns and tests.

Representative contribution: **PR #22**, turning a real Alexa Local Inspector request-shape mismatch into a bounded compatibility fix, regression test, protocol negotiation verification, MCP App discovery check and reusable remote probe.

Required Devpost fields are frozen in `docs/OPEN_SOURCE_SUBMISSION.md`.

## Bonus — friction log

`docs/FRICTION_LOG.md` contains real development friction with the complete required fields: task, steps, expected vs actual result, severity, workaround and actionable suggestion.

The final Devpost submission should provide the direct public friction-log URL so the project is eligible for the announced judging bonus.

## Evidence rule

Marketing copy does not count. Each important claim must map to executable tests, public runtime behavior, live provider receipts/readback, exact-SHA AWS evidence, a remote gate, or an explicit simulation/non-live disclosure.
