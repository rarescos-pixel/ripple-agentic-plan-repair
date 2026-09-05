# Amazon judging rubric mapping — current competition build

Ripple is audited against the four equally weighted hackathon criteria. Evidence is separated from claims; simulated provider behavior and not-yet-live AWS/Alexa surfaces are disclosed explicitly.

## 1. Technical Implementation

**Current strength: high.**

Evidence:

- public MCP `2025-11-25` Streamable HTTP endpoint;
- OAuth protected-resource / authorization-server discovery;
- service credentials plus authorization-code + PKCE S256 user flow;
- Alexa-compatible refresh-token path with wrong-resource rejection;
- five bounded MCP tools: record, preview, approve, execute, status;
- dependency traversal across heterogeneous commitments;
- deterministic net-value optimization;
- exact snapshot approval and zero-write preapproval phases;
- provider preflight, idempotency keys and authoritative receipts;
- interruption/restart recovery and duplicate-free replay;
- money-first Repair Card implemented as a real MCP App resource;
- independent remote authenticated MCP smoke: PASS;
- independent Alexa package/store-media gate: PASS;
- deterministic release/adversarial gate: PASS;
- CI validation for MCP protocol, Alexa Local Inspector request-shape compatibility, MCP App safety, Alexa package, CloudFormation, AWS credential lifecycle, submission surfaces and evidence drift.

**Known remaining gap:** AWS components are implemented and AWS-ready but not yet claimed live. A live AWS score gain is accepted only after Bedrock + DynamoDB + CloudWatch + IAM/Budget are provisioned/exercised and the public Railway runtime passes post-cutover restart/replay evidence.

## 2. Design

**Current strength: high, but final score depends heavily on the recorded demo.**

Design contract:

- one utterance captures the changed fact;
- the first decision surface is money-first: affected commitments, dollars at risk, repair cost and net value preserved;
- voice summary, visual card, accessibility label and CTA disclose the same exact approval;
- the Repair Card uses human-readable commitment names rather than technical IDs;
- the MCP App is display-only: visual polish cannot bypass approval or execute tools;
- material drift forces re-approval;
- unresolved or expired work remains explicit;
- the final video is judge-first: customer outcome within 20 seconds, technical architecture later.

Primary remaining design evidence: official Alexa+ onboarding/inspection if accessible and the final <3-minute video.

## 3. Potential Impact

**Current strength: high and unusually measurable for an assistant workflow.**

Golden consumer fixture:

- **5** downstream commitments affected;
- **$116** direct avoidable loss;
- **$42** repair cost;
- **$74** net direct cash preserved.

Event Operations fixture:

- **$5,800** avoidable loss;
- **$620** repair cost;
- **$5,180** net direct cash preserved.

Why this is credible rather than generic “productivity” language:

- Ripple explicitly prices the consequence set and the repair;
- optimization maximizes net preserved value rather than minimizing repair cost;
- consumer travel is a narrow demo wedge, while the dependency/economic engine is generic;
- provider transactions remain deterministic simulations and the fixture dollars are disclosed as scenario values, not market statistics.

The commercial path can extend to premium travel concierge, corporate travel, hospitality recovery, insurance, event operations and executive assistance without changing the core consequence-repair primitive.

## 4. Quality of the Idea

**Current strength: top-tier target.**

Ripple is not a basic MCP wrapper or single-turn information tool. Its primitive is **cascading consequence repair**:

> one real-world state change invalidates part of a dependency graph; Ripple identifies only the affected commitments, quantifies exposure, selects the safe repair that preserves the most value, obtains one exact approval and executes with durable receipts.

The Alexa+ fit is structural:

- voice captures the one changed fact during divided-attention moments;
- state/dependencies carry context beyond a single question;
- the workflow orchestrates across multiple service types;
- the Repair Card complements voice with an exact money/approval surface;
- bounded authority and replay safety make agentic action credible rather than merely impressive.

## AWS Builder mini challenge

Target only after live verification.

The AWS architecture is deliberately structural rather than a single decorative model call:

- Bedrock performs constrained language normalization only;
- DynamoDB makes approvals/idempotency/receipts durable;
- CloudWatch stores redacted evidence traces;
- IAM scopes runtime authority;
- Budgets constrains spend.

The repository is AWS-ready. A competitive AWS Builder claim is unlocked only by the live benchmark, real resource verification, Railway cutover and fresh-session replay proof.

## Open Source mini challenge

**Eligible low-risk additional target.**

Ripple is a new public MIT-licensed repository created during the hackathon window, not a pre-existing project with a formatting-only contribution. The repository publishes the complete project plus reusable safety/interoperability patterns and tests.

Representative contribution: **PR #22**, which turns a real Alexa Local Inspector request-shape mismatch into:

- a bounded interoperability fix;
- a regression test reproducing the documented request sequence;
- protocol negotiation verification;
- `ui://` MCP App discovery verification;
- a reusable remote probe;
- an evidence-linked friction-log entry.

Required Devpost fields are frozen in `docs/OPEN_SOURCE_SUBMISSION.md`.

## Bonus — friction log

`docs/FRICTION_LOG.md` contains real development friction with the complete required fields: task, steps, expected vs actual result, severity, workaround and actionable suggestion.

Current entries cover:

1. Alexa-compatible OAuth refresh behavior;
2. MCP App visual resource binding;
3. add-on package/public-media preflight;
4. least-privilege AWS credentials for an external PaaS runtime;
5. Alexa Local Inspector JSON-only `Accept` request-shape interoperability.

No friction entry is fabricated solely to chase bonus points.

## Evidence rule

Marketing copy does not count. Each important claim must map to executable tests, public runtime behavior, receipts/logs, a remote gate, or an explicit simulation/non-live disclosure.
