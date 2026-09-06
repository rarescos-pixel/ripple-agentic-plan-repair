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

Ripple replies:

> **5 commitments are affected. $116 is at risk. Ripple can repair the cascade for $42 and preserve $74. Approve $42 repair?**

After approval, Ripple executes only the disclosed actions, returns five authoritative receipts and makes an exact replay produce zero duplicate provider writes.

## What Ripple does

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

If an official Alexa+ production client is unavailable for the final demo, Ripple will use the rules-permitted simulated Alexa+ experience backed by the real public MCP server. No actual Alexa+ production-client session is claimed unless it is actually exercised.

## Golden scenario

- 5 downstream impacts
- $116 direct avoidable loss
- $42 repair cost
- $74 net direct cash preserved
- 0 writes before approval
- 0 writes during approval
- 5 authoritative execution receipts
- exact replay: **5/5 deduplicated**
- fresh-session replay: authoritative unique-write count remains **5 → 5**, proving **0 new provider writes**

These are deterministic scenario fixture values, not market claims.

## Generality proof
Event Operations models a conference-time change across AV delivery, catering, VIP transport, security staffing and a sponsor briefing:

- $5,800 avoidable loss
- $620 repair cost
- **$5,180 net cash preserved**

A cheaper repair option is intentionally included but rejected because it preserves less net value. This proves the engine is consequence/economic-repair logic rather than a flight-specific workflow.

## Implemented and verified

- public self-hosted MCP endpoint using protocol `2025-11-25` over Streamable HTTP;
- stateful sessions, protocol-version enforcement and Origin validation;
- OAuth discovery, service credentials, authorization-code + PKCE S256 and refresh-token flow;
- Alexa-compatible refresh behavior with an explicitly wrong resource rejected;
- five bounded MCP tools: record, preview, approve, execute and status;
- deterministic dependency graph and money-aware repair selection;
- exact-content approval binding to cost, scope and snapshot;
- zero-write preview and approval phases;
- provider preflight, idempotency keys and authoritative receipts;
- exact approved-plan recovery across MCP process/session restart with owner binding and duplicate suppression;
- money-first display-only MCP App Repair Card;
- Alexa+ package assets, six icon sizes, 600×900 carousel, privacy and terms;
- **one bounded real external provider proof** through GitHub Issues: write/readback/replay-dedup/restore PASS at provider cost $0;
- deterministic release gate and adversarial/failure matrix: PASS;
- live AWS structural services: Nova 2 Lite, DynamoDB and CloudWatch;
- canonical public AWS runtime on ECS Express Mode / Fargate with task roles and exact-SHA release proof.

## Public runtime

Base: `https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws`

MCP endpoint: `https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws/mcp`

The Alexa+ add-on package points to the same canonical endpoint.

## AWS Builder

**AWS services are live and structurally verified, and the canonical public runtime runs on AWS.**

- **Amazon ECS Express Mode / Fargate** — canonical public HTTPS MCP runtime;
- **Amazon Bedrock / Nova 2 Lite** — changed-fact normalization only;
- **Amazon DynamoDB** — durable proposal/approval state, idempotency records and authoritative receipts;
- **Amazon CloudWatch Logs** — redacted structured traces;
- **IAM task roles + GitHub OIDC** — runtime/deployment identity without committed static AWS credentials;
- **AWS Budgets / anomaly controls** — cost guardrails.

The exact-SHA release proof binds the Git commit to an immutable ECR digest, ECS task definition and repeated public `/readyz` source-revision checks. It then runs authenticated MCP/OAuth smoke, live Bedrock normalization and a fresh-session DynamoDB replay proof. `5/5 deduplicated` plus an unchanged authoritative write count (`5 → 5`) is the direct evidence for zero new provider writes on replay. CloudWatch traces and ECR digest readback close the proof.

## Open Source Mini Challenge

Ripple is a **new MIT-licensed public project created during the hackathon submission window**.

- **Contribution URL:** `https://github.com/rarescos-pixel/ripple-agentic-plan-repair/pull/22`
- **Project repository URL:** `https://github.com/rarescos-pixel/ripple-agentic-plan-repair`
- **GitHub username:** `rarescos-pixel`

See `docs/OPEN_SOURCE_SUBMISSION.md` for the required what/how/why packet.

## Trust and disclosure

Real running software/evidence: AWS-hosted MCP transport, OAuth/PKCE, dependency analysis, economic optimization, approval boundary, durable recovery, receipts, replay suppression, MCP App, Alexa package/media surfaces, one bounded real GitHub Issues provider, and live Bedrock/DynamoDB/CloudWatch runtime behavior.

Deterministic simulated integrations: airline, ride, reservation, delivery, pet-care and calendar provider adapters. Ripple does not claim real third-party bookings, payments or market prices. Example dollar values are deterministic fixtures.

**No actual Alexa+ production-client session is claimed** unless the official onboarding/inspection path is actually exercised.

## Product feedback / friction

The project includes real friction evidence covering Alexa-compatible OAuth refresh, MCP App rendering contracts, add-on media validation, Local Inspector request-shape interoperability, AWS identity boundaries and ECS infrastructure-role identity continuity.

## Open source

Public GitHub repository, MIT licensed. Repository created on **2026-09-04**, inside the hackathon submission window that began on **2026-08-31**.
