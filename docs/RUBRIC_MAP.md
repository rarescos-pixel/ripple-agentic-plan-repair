# Amazon judging rubric mapping — winner-build state

Ripple is audited against the four equally weighted hackathon criteria. Claims are separated from observed evidence. Simulated provider behavior and the still-pending public Railway AWS-backend cutover are disclosed explicitly.

## 1. Technical Implementation

**Current strength: very high / freeze candidate.**

Verified evidence:

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
- independent remote authenticated MCP smoke: PASS;
- exact-revision Railway production proof on source SHA `58898530b40564e1b0025db4ac8ea7d2f9249817`: PASS;
- independent Alexa package/store-media gate: PASS;
- adversarial/failure-truth matrix: PASS;
- direct AWS structural evidence: GitHub OIDC PASS, Nova 2 Lite live inference PASS, DynamoDB live receipt/replay PASS, CloudWatch Logs write+readback PASS;
- CI validation for MCP protocol, Alexa request-shape compatibility, MCP App safety, Alexa package, CloudFormation, AWS evidence/lifecycle, submission surfaces and generated evidence drift.

**Remaining technical gap:** the canonical public Railway process is not yet claimed to use Bedrock + DynamoDB + CloudWatch for every request. That stronger runtime cutover requires a credential-safe external-workload identity path and must not be achieved by leaking static AWS credentials or weakening the working endpoint. Direct structural AWS evidence is already live and independently verified.

## 2. Design

**Current strength: very high; final perceived score is now mostly a video/presentation problem.**

Design contract:

- one utterance captures the changed fact;
- first decision surface is money-first: affected commitments, dollars at risk, repair cost and net value preserved;
- voice summary, visual card, accessibility label and CTA disclose the same exact approval;
- Repair Card uses human-readable commitment names rather than technical IDs;
- “Why this plan?” is emitted only when the economic comparison is mechanically provable;
- execution result returns a sanitized receipt timeline, making new writes and replay dedup visible;
- MCP App is display-only: polish cannot bypass approval or execute tools;
- material drift forces re-approval;
- unresolved or expired work remains explicit;
- restart recovery preserves the exact already-approved authority rather than silently widening it.

Remaining design work is **VIDEO LOCKED** and must be done with the owner: the final sub-3-minute narrative must make this sophistication obvious without turning into a technical walkthrough.

## 3. Potential Impact

**Current strength: very high and unusually measurable for an assistant workflow.**

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
- a cheaper-but-worse alternative is executable evidence in the Event Operations scenario;
- consumer travel is a narrow hero wedge while the dependency/economic engine is generic;
- dollar amounts are explicitly deterministic scenario fixtures, not market statistics;
- a bounded real provider proof demonstrates that the execution/receipt contract is not simulation-only.

Applicable domains without changing the primitive include travel concierge, corporate travel, hospitality recovery, event operations, insurance workflows, executive assistance and other dependency-heavy operations.

## 4. Quality of the Idea

**Current strength: top-tier target.**

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

**Direct structural AWS live evidence: VERIFIED.**

- Bedrock / Nova 2 Lite: constrained language normalization, live invocation PASS;
- DynamoDB: durable state/idempotency contract, live receipt write/readback and conditional replay rejection PASS;
- CloudWatch Logs: redacted structured trace write + readback PASS;
- IAM / GitHub OIDC: temporary bounded evidence-run credentials without committed static keys;
- Budgets / anomaly controls: bounded-spend guardrails.

The precise claim boundary is:

> **AWS services are live and structurally verified; the canonical public Railway AWS-runtime cutover is pending.**

This is stronger and more truthful than either a diagram-only AWS claim or pretending the public process has completed a cutover it has not.

## Open Source mini challenge

**Eligible / submission-ready.**

Ripple is a new public MIT-licensed repository created during the hackathon window, not a pre-existing project with a formatting-only contribution. The repository publishes the complete project plus reusable safety/interoperability patterns and tests.

Representative contribution: **PR #22**, turning a real Alexa Local Inspector request-shape mismatch into a bounded compatibility fix, regression test, protocol negotiation verification, MCP App discovery check and reusable remote probe.

Required Devpost fields are frozen in `docs/OPEN_SOURCE_SUBMISSION.md`.

## Bonus — friction log

`docs/FRICTION_LOG.md` contains real development friction with the complete required fields: task, steps, expected vs actual result, severity, workaround and actionable suggestion. Entries cover OAuth refresh interoperability, MCP App binding, package/media preflight, AWS credentials for an external PaaS and Local Inspector request-shape compatibility.

No friction entry is fabricated solely to chase bonus points.

## Evidence rule

Marketing copy does not count. Each important claim must map to executable tests, public runtime behavior, live provider receipts/readback, AWS live evidence, a remote gate, or an explicit simulation/non-live disclosure.
