# Bedrock normalization benchmark protocol

## Models under test

- `eu.amazon.nova-lite-v1:0`
- `eu.amazon.nova-2-lite-v1:0`

Both are evaluated through Amazon Bedrock `Converse` with the same forced `record_change` tool schema, temperature 0, identical canonical context, and the same output-token ceiling.

## What is measured

Each case must match exactly:

- canonical `node_id`;
- whitelisted `field`;
- normalized `new_value`.

A low-confidence response, invalid tool call, invented node/field, exception, or wrong normalized value is a failed case.

The harness also records model-reported input/output token counts and wall-clock latency.

## Selection rule

1. highest exact accuracy;
2. if tied, lowest total input + output tokens;
3. if still tied, lowest median latency.

This intentionally prevents a slightly cheaper model from winning when it is less reliable at the one Bedrock task Ripple delegates.

## CI vs live evidence

CI uses deterministic fake clients only to prove the benchmark machinery and ranking policy. CI results must never be presented as Nova model performance.

A model is locked only after `scripts/bedrock_benchmark.py` runs against real Bedrock and the resulting `docs/BEDROCK_BENCHMARK_LIVE.md` is reviewed for errors and outliers.
