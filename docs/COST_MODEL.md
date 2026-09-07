# Ripple — Cost Model and Economic Guardrails

## Principle

Ripple should preserve more customer value than it costs to run or to repair a plan. Cost is therefore part of the decision policy, not merely an infrastructure concern.

For each repair option the deterministic planner ranks by:

1. hard safety/user constraints;
2. **maximum net cash preserved = avoidable loss - added repair cost**;
3. lower added cost when net preservation ties;
4. reversible action when the economic result still ties;
5. deterministic operation-name tie-break.

This prevents a superficially free action that saves little value from beating a slightly paid action that prevents a much larger loss.

## Canonical public runtime cost shape

Ripple's canonical public runtime is AWS-hosted on **Amazon ECS Express Mode / Fargate**, with **Amazon Bedrock / Nova 2 Lite**, **Amazon DynamoDB**, and **Amazon CloudWatch Logs** structurally active.

The frozen task definition uses the minimum current application envelope required by this deployment:

- **0.25 vCPU**
- **0.5 GB memory**
- public HTTPS through the ECS Express-managed ingress/load-balancing path

ECS Express Mode itself is an orchestration convenience rather than a separate application runtime product: the underlying Fargate compute, load-balancing, logging, storage and network services remain the billable surfaces.

Ripple therefore does **not** claim to be the cheapest possible way to host a demo. The design choice is justified by correctness and evidence:

- Fargate provides the canonical public runtime;
- DynamoDB makes exact proposals, approvals, idempotency records and authoritative receipts durable;
- Bedrock handles only the narrow natural-language normalization boundary;
- CloudWatch stores redacted structured execution traces;
- IAM task roles and GitHub OIDC avoid committed static AWS access keys.

The correct optimization target is **minimum reliable cost for the required correctness boundary**, not minimum headline hosting price.

## Model-call envelope

Ripple's Bedrock interpretation boundary is deliberately narrow:

- at most one model call per proposed change;
- maximum combined input envelope: 8,000 characters;
- maximum model output: 256 tokens;
- the model may normalize the changed fact but does not own old state, repair policy, money arithmetic, approval, or execution.

For planning purposes, using a conservative 2,000 input-token + 256 output-token event envelope:

| Model | Published input rate | Published output rate | Approx. cost / change event | 10k events | 100k events |
|---|---:|---:|---:|---:|---:|
| Amazon Nova 2 Lite | $0.30 / 1M | $2.50 / 1M | ~$0.00124 | ~$12.40 | ~$124.00 |
| Amazon Nova Lite | $0.06 / 1M | $0.24 / 1M | ~$0.000181 | ~$1.81 | ~$18.14 |

These are planning-envelope estimates based on the recorded pricing snapshot, not measured invoices. Typical Ripple utterances should be materially smaller.

Decision: do **not** trade away interpretation accuracy merely to save fractions of a cent in the hackathon demo. Benchmark cheaper models only if normalization accuracy remains equivalent.

## Durable-state and observability cost shape

The structural AWS runtime uses pay-per-use services where they improve correctness:

- **DynamoDB on-demand** for proposal/approval state, idempotency keys and authoritative receipts;
- **Bedrock** for one constrained changed-fact normalization call per change event;
- **CloudWatch Logs** for redacted structured trace evidence;
- **ECS Express Mode / Fargate** for the canonical public MCP transport.

This means the always-available baseline is dominated by the container/load-balancing footprint rather than by Ripple's very small model-call or state-write volume at hackathon scale.

That is acceptable because the infrastructure is doing real correctness work. None of these services is included for decorative logo value.

## Budget guard

Ripple maintains explicit AWS spend guardrails. The verified deployment uses an account-level low-dollar budget/anomaly safety mechanism for this hackathon environment. Alerts are guardrails, not a hard service cutoff.

The repository also contains CloudFormation budget parameters for reproducible deployment paths. Those template defaults must not be confused with the separately verified live-account guard.

Resource tags remain useful for attribution, but the safety control is intentionally not dependent on cost-allocation-tag activation timing.

## Historical Railway baseline — audit history only

Before the AWS cutover, Ripple was smoke-tested on Railway. Historical measurements showed extremely low idle application consumption and a practical billing floor dominated by the Railway plan minimum.

Those numbers remain useful as audit history and as evidence that Ripple's application process itself is lightweight, but **Railway is no longer the canonical runtime and no current judge-facing claim should present it as such**.

The architecture was intentionally moved to AWS because the final submission benefits from one exact, judge-verifiable runtime boundary that proves:

- source SHA;
- immutable container digest;
- ECS task definition;
- public readiness;
- live Bedrock normalization;
- DynamoDB durability/replay;
- CloudWatch trace emission;
- authenticated MCP/OAuth behavior.

That evidence gain is more important than preserving the smallest possible hosting bill during judging.

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
- an economically inferior zero-cost AV option is rejected in favor of the option that preserves more net value

These values are deterministic scenario fixtures. They demonstrate the optimizer and approval surface; they are **not** market-price claims, TAM claims, or subscription ROI claims.

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

The commercial KPI is not "messages answered". It is **cash/time/commitments preserved per change event**, with a visible ratio between avoidable loss and repair cost.

## Cost narrative for judges

The judge-facing message should stay simple:

> Ripple spends model and infrastructure cost only where it buys correctness. Bedrock is narrow and bounded; DynamoDB, CloudWatch and Fargate exist because durable approval, duplicate-safe execution and public evidence are part of the product.

Do not lead the demo with hosting cost. Lead with customer value, then show that the architecture is deliberately bounded and economically sane.
