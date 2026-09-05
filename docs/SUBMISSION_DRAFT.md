# Devpost Submission Draft — current evidence-bounded version

## Project name
Ripple

## Tagline
**Tell Alexa one thing that changed. Ripple fixes what breaks downstream.**

## One-sentence pitch
Ripple is a money-aware consequence-repair layer for Alexa+: it turns one changed fact into a safe, economically optimized repair of every downstream commitment it actually affects — without making the customer open five separate apps or sites.

## Track selections

- **Primary Track:** Alexa+
- **Mini Challenge:** AWS Builder
- **Mini Challenge:** Open Source

## The problem
Plans rarely break one thing. A cancelled flight can invalidate a ride, dinner reservation, grocery delivery, pet-care window and tomorrow's meeting. The user must discover the cascade manually while already dealing with the original disruption.

## The experience
The user says:

> “Our flight home was cancelled. We’ll land tomorrow at six.”

Ripple replies with the decision that matters:

> **5 commitments are affected. $116 is at risk. Ripple can repair the cascade for $42 and preserve $74. Approve $42 repair?**

After approval, Ripple executes only the disclosed actions, returns five authoritative receipts and makes an exact replay produce zero duplicate provider writes.

## What Ripple does
Ripple:

1. normalizes one changed fact;
2. propagates it through a dependency graph;
3. identifies only commitments now invalid or at risk;
4. evaluates declarative repair options by **avoidable loss − repair cost**;
5. applies deterministic safety/policy rules;
6. presents one money-first Repair Card and exact approval;
7. executes bounded idempotent actions;
8. records authoritative receipts and leaves unresolved work visible.

The model never chooses the money-spending repair and never receives write authority.

## Why Alexa+
Disruptions are divided-attention moments when opening five apps is the wrong interface. One utterance captures the changed fact; one compact voice + visual proposal explains the cascade; one exact approval authorizes only that snapshot.

Ripple uses Alexa+'s self-hosted MCP path as an agentic orchestration surface rather than as a Q&A wrapper. The Repair Card is a real MCP App resource, so screen and voice expose the same consequences, money and approval boundary.

For the final demo, if an official Alexa+ client is unavailable, Ripple will use the rules-permitted **simulated Alexa+ experience backed by the real public MCP server**. This keeps the customer/agent conversation central while preserving a real runtime integration instead of a fake screenshot.

## Golden scenario

- 5 downstream impacts
- $116 direct avoidable loss
- $42 repair cost
- $74 net direct cash preserved
- 0 writes before approval
- 0 writes during approval
- 5 authoritative execution receipts
- exact replay: 5/5 deduplicated, still only 5 unique writes

These are deterministic scenario fixture values, not market claims.

## Generality proof
The second scenario is Event Operations: a conference-time change affects AV delivery, catering, VIP transport, security staffing and a sponsor briefing.

- $5,800 avoidable loss
- $620 repair cost
- $5,180 net cash preserved

A cheaper repair option is intentionally included but rejected because it preserves less net value. This proves the engine is consequence/economic-repair logic rather than a flight-specific workflow.

## Implemented and verified

- public self-hosted MCP endpoint using protocol `2025-11-25` over Streamable HTTP;
- stateful sessions, protocol-version enforcement and Origin validation;
- OAuth discovery, service credentials, authorization-code + PKCE S256 and refresh-token flow;
- Alexa-compatible refresh behavior with an explicitly wrong resource still rejected;
- five bounded MCP tools: record, preview, approve, execute and status;
- deterministic dependency graph and money-aware repair selection;
- exact-content approval binding to cost, scope and snapshot;
- zero-write preview and zero-write approval phases;
- provider preflight, idempotency keys and authoritative receipts;
- interruption/restart recovery with duplicate suppression;
- money-first Repair Card with voice/visual parity;
- display-only MCP App resource via `ui://` + `text/html;profile=mcp-app`;
- Alexa+ package assets, six icon sizes, 600×900 carousel, privacy and terms;
- independent remote authenticated smoke from a separate Railway container: PASS;
- remote flow: 0 preview writes, 0 approval writes, 5 receipts at execute, 5/5 deduplicated on replay;
- independent remote store-media gate: PASS;
- deterministic release gate and adversarial matrix: PASS;
- public CI covering core tests, MCP conformance, MCP App safety, Alexa package, CloudFormation, AWS credential lifecycle and evidence drift.

## Public runtime

MCP endpoint: `https://ripple-v12-production.up.railway.app/mcp`

Judge evidence is linked from the repository README, including `ALEXA_REMOTE_EVIDENCE.md`, `REMOTE_SMOKE_REPORT.md`, `VALIDATION_REPORT.md`, `EVIDENCE_MATRIX.md` and `RUBRIC_MAP.md`.

## AWS Builder
Ripple keeps the public MCP host on Railway and uses AWS only where it is structural:

- Amazon Bedrock — changed-fact normalization only;
- Amazon DynamoDB — durable approvals, idempotency records and authoritative receipts;
- Amazon CloudWatch Logs — redacted structured traces;
- IAM — resource-scoped runtime policy;
- AWS Budgets — project cost guardrails.

The IaC, adapters, benchmark harness, runtime cutover, least-privilege credential lifecycle and live verification scripts are implemented and CI-validated. **Current evidence status is AWS-ready, not AWS-live verified.** The final submission will claim live AWS use only after the real stack, Railway cutover and post-restart replay proof pass on one source SHA.

## Open Source Mini Challenge

Ripple is a **new MIT-licensed public project created during the hackathon submission window**.

Required fields:

- **Contribution URL:** `https://github.com/rarescos-pixel/ripple-agentic-plan-repair/pull/22`
- **Project repository URL:** `https://github.com/rarescos-pixel/ripple-agentic-plan-repair`
- **GitHub username:** `rarescos-pixel`

What I did / how it works / why it matters is captured in `docs/OPEN_SOURCE_SUBMISSION.md`.

The contribution is not a README-only change. The public project includes the complete MCP consequence-repair engine, exact-approval and replay-safety patterns, MCP App integration, OAuth interoperability, AWS infrastructure/lifecycle tooling, adversarial tests and reproducible remote probes. PR #22 is supplied as a representative concrete contribution because it turns a real Alexa Local Inspector interoperability mismatch into an integration test, bounded compatibility fix and reusable remote probe.

## Trust and disclosure
Real running software: MCP transport, OAuth/PKCE, dependency analysis, economic optimization, approval boundary, execution ledger, receipts, replay suppression, MCP App and Alexa package/media surfaces.

Deterministic simulated integrations: airline, ride, reservation, delivery, pet-care and calendar provider adapters. Ripple does not claim real third-party bookings or payments.

No actual Alexa+ production-client session is claimed unless the official onboarding/inspection path is successfully exercised. The hackathon rules explicitly allow the simulated Alexa+ experience path, so official client access is not treated as a prerequisite. No live Bedrock/DynamoDB/CloudWatch runtime is claimed until the AWS live gate passes.

## Product feedback / friction
The project includes real friction-log entries covering Alexa-compatible OAuth refresh behavior, MCP App rendering contracts, add-on package/media validation, least-privilege AWS credentials for an external PaaS runtime and Local Inspector request-shape interoperability. Each entry includes steps, expected vs actual behavior, severity, workaround and an actionable suggestion.

## Open source
Public GitHub repository, MIT licensed. The repository was created on **2026-09-04**, after the hackathon submission period opened on **2026-08-31**. The project and its tests/integration patterns were created during the hackathon window.
