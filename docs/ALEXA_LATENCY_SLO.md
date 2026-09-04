# Alexa+ MCP latency SLO

## External requirement

Amazon's Alexa+ MCP QuickStart currently requires the MCP server to meet a round-trip query response latency of **less than 500 ms**:

- https://www.developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-quickstart.html

This repository treats that as a strict per-sample limit for deployment evidence rather than a p95-only target.

## Executable probe

`scripts/mcp_latency_probe.py` performs authenticated real-HTTP measurements after OAuth and MCP session setup. It measures these non-destructive customer-path operations independently:

- `ping`
- `tools/list`
- `record_change`
- `preview_repair_plan`
- `get_repair_status`

Defaults:

```text
RIPPLE_LATENCY_LIMIT_MS=500
RIPPLE_LATENCY_SAMPLES=20
RIPPLE_LATENCY_WARMUP=2
```

A probe passes only when **every measured round trip** is below the configured limit. It reports p50, p95, max, and under-limit counts so a single slow response cannot be hidden by an aggregate percentile.

## Evidence boundary

The deterministic CI suite tests the gate semantics and syntax-checks the remote probe. CI does **not** claim Internet latency. A deployment is only labeled latency-verified after the probe is run from an independent remote worker against the public HTTPS MCP endpoint and the resulting measurements are captured.

The current non-destructive probe intentionally excludes approval and execution writes. Those are tracked separately because provider/AWS write latency has different side-effect and cost semantics. Before a live AWS cutover is considered Alexa-ready, the critical Bedrock normalization path must also be measured against this 500 ms requirement rather than assumed compliant.
