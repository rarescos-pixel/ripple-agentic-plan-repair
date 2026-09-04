# Ripple v1.4 cost model

Cost is a product constraint, not an afterthought.

## Current hosting

The canonical MCP runtime remains on Railway because measured idle usage is extremely small. Do not migrate the orchestration server to a more expensive AWS runtime merely to increase AWS surface area.

## AI boundary

Models may normalize a reported change and produce bounded natural-language phrasing. They do not own money calculations, dependency evaluation, option ranking, approval scope, provider side effects, idempotency or authoritative receipts.

## Durable-state request economics

For a five-action repair:

- 1 approval write;
- 5 idempotency reads;
- at most 5 authoritative receipt writes;
- no scans;
- no model call for deterministic ranking or arithmetic.

## Economic decision rule

Allowed repair options are ranked by net direct cash preserved:

```text
avoidable_loss - added_cost
```

Then by lower repair cost, reversibility and deterministic tie break.

## AWS budget guardrail

The first live AWS milestone should use DynamoDB on-demand, the smallest Bedrock model that passes the normalization evaluation set, short CloudWatch retention and an AWS Budget alarm before load testing. A service is not added unless it materially improves judging evidence, reliability, safety, cost or user value.
