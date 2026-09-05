# Ripple — Cost Model and Economic Guardrails

## Principle

Ripple should preserve more customer value than it costs to run or to repair a plan. Cost is therefore part of the decision policy, not only an infrastructure concern.

For each repair option the deterministic planner ranks by:

1. hard safety/user constraints;
2. **maximum net cash preserved = avoidable loss - added repair cost**;
3. lower added cost when net preservation ties;
4. reversible action when the economic result still ties;
5. deterministic operation-name tie-break.

This prevents a superficially free action that saves little value from beating a slightly paid action that prevents a much larger loss.

## Current public runtime cost

Observed Railway `ripple-v12` metrics on 2026-09-04 over a one-hour window:

- average CPU: `0.0015677 vCPU`
- average memory: `0.0226319 GB` (~22.6 MB)
- sampled network RX/TX: effectively zero during the idle measurement window

Using Railway's published resource rates ($20/vCPU-month and $10/GB-month), that idle resource envelope is about **$0.26/month** before plan minimums and traffic.

Railway Hobby currently has a **$5/month minimum/included-usage commitment**, so at the measured baseline the practical hosting bill is expected to be dominated by the $5 plan minimum rather than by Ripple compute.

Decision: **KEEP the verified Railway MCP transport for the primary Alexa+ demo.** Moving the public transport only to claim AWS usage would increase cost and regression risk without increasing customer value.

## Model-call envelope

Ripple's Bedrock interpretation boundary is deliberately narrow:

- at most one model call per proposed change;
- maximum combined input envelope: 8,000 characters;
- maximum model output: 256 tokens;
- model may normalize the changed fact but does not own old state, repair policy, money arithmetic, approval, or execution.

For planning purposes, using a deliberately conservative 2,000 input-token + 256 output-token event envelope:

| Model | Published input rate | Published output rate | Approx. cost / change event | 10k events | 100k events |
|---|---:|---:|---:|---:|---:|
| Amazon Nova 2 Lite | $0.30 / 1M | $2.50 / 1M | ~$0.00124 | ~$12.40 | ~$124.00 |
| Amazon Nova Lite | $0.06 / 1M | $0.24 / 1M | ~$0.000181 | ~$1.81 | ~$18.14 |

These are upper-envelope planning estimates, not measured production bills. Typical Ripple utterances should be materially smaller.

Decision: do **not** trade away interpretation accuracy merely to save fractions of a cent in the hackathon demo. Benchmark Nova Lite against Nova 2 Lite first; use the cheaper model only if accuracy remains equivalent on the change-normalization test set.

## Durable-state AWS cost shape

The structural AWS runtime uses serverless/pay-per-use components where they improve correctness:

- DynamoDB on-demand for approval state, idempotency keys, and authoritative receipts;
- Bedrock invoked directly from the Railway-hosted Ripple runtime for the narrow normalization boundary;
- CloudWatch Logs for redacted structured trace evidence.

There is no Lambda/ECS/Fargate layer in the locked architecture because it would add cost and operational surface without a demonstrated correctness or scoring gain.

## Budget guard — account-wide by design

Ripple provisions a **$10/month AWS Budget** with actual-cost alerts at **50%, 80%, and 100%**.

The budget intentionally has **no tag-based CostFilters**. AWS requires user-defined resource tags to be activated as cost-allocation tags before they can be used for budget filtering, and a new tag can take time to become available and active. Depending on that activation during the hackathon live bootstrap would weaken the guard exactly when it is most useful.

Instead:

- the budget covers the **whole AWS account** immediately;
- Ripple resources still carry `Project=Ripple` and environment tags for attribution/evidence;
- the live verifier rejects a budget that unexpectedly depends on CostFilters;
- if the account later hosts unrelated workloads, a project-scoped reporting budget can be added after cost-allocation tags are active, without replacing the account-wide safety guard.

This is intentionally conservative because the hackathon account's primary requirement is **bounded spend with minimal setup dependency**.

## Why not move the MCP endpoint to ECS/Fargate now

ECS/Fargate would create additional persistent/container, load-balancing, monitoring and transfer cost surfaces. Fargate also bills requested vCPU/memory rather than Ripple's observed tiny idle consumption. The smallest continuous task therefore has a materially higher baseline than the measured Railway service before ancillary resources are counted.

Decision: **AWS should strengthen the architecture, not replace a working low-cost transport for logo value.**

## Customer-economics proof fixtures

### Consumer travel cascade — golden demo

- direct avoidable loss: **$116**
- added repair cost: **$42**
- net direct cash preserved: **$74**
- external writes before approval: **0**

### Event-operations cascade — generality/economic fixture

A conference start-time shift affects AV delivery, catering, VIP transport, security staffing, and a sponsor briefing.

- affected commitments: **5**
- direct avoidable loss: **$5,800**
- added repair cost: **$620**
- net direct cash preserved: **$5,180**
- sponsor attendees notified: **8**
- economically inferior zero-cost AV option is rejected in favor of the option that preserves more net value

This second fixture is executable evidence that the engine is not flight-specific and that the same policy can protect materially larger business commitments.

## Commercial direction

The strongest economic path is not to turn Ripple into another booking provider. It is to become the **consequence-repair layer across existing actions and providers**.

Consumer wedge:

- travel disruption;
- reservations;
- rides;
- delivery;
- local/home services;
- calendar and people commitments.

Higher-value B2B/B2B2C expansion:

- travel and hospitality disruption management;
- corporate travel / executive assistance;
- loyalty and premium-card concierge;
- travel insurance assistance;
- event and venue operations;
- hospitality guest recovery.

The commercial KPI is not "messages answered". It is **cash/time/commitments preserved per change event**, with a visible ratio between avoided loss and repair cost.
