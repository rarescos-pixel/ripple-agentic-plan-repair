# Judge Runbook — fastest path to Ripple evidence

The repository is designed so the project can be understood without running anything, while still making every important claim reproducible.

## 20 seconds — understand the product

Read the top of the README:

> **One thing changed → 5 commitments affected → $116 at risk → repair for $42 → preserve $74 → approve?**

Ripple is a money-aware consequence-repair layer for Alexa+. It is not a generic Q&A wrapper.

## 60 seconds — inspect the public proof

Public MCP:

`https://ripple-v12-production.up.railway.app/mcp`

Evidence already captured from an **independent remote container**:

```text
Ripple authenticated MCP smoke: PASS
protocol: 2025-11-25
preview: 5 impacts / 0 writes
approval writes: 0
execute: 5 receipts / 5 unique writes
replay: 5 deduplicated / 5 unique writes
```

See:

- `docs/ALEXA_REMOTE_EVIDENCE.md`
- `docs/REMOTE_SMOKE_REPORT.md`
- `docs/MCP_APP_EVIDENCE.md`

The Alexa store-media gate separately verifies the 600×900 carousel, six icon dimensions, privacy/terms and canonical MCP endpoint.

## 90 seconds — run the deterministic release proof

```bash
python -m pip install -e . pytest
PYTHONPATH=src python -m ripple.evaluation.release_gate
```

Expected: `Overall: PASS`.

The gate verifies:

- golden 5-impact cascade;
- $116 risk / $42 repair / $74 net preserved;
- money-first Repair Card parity;
- zero writes before approval;
- exact-content approval disclosure;
- bounded execution and idempotent replay;
- missed deadline truthfulness;
- ambiguous-provider fail-closed behavior;
- hard preferences before optimization;
- Event Operations economic-choice scenario;
- content drift re-approval;
- interruption recovery with zero duplicate writes.

Canonical generated report: `docs/VALIDATION_REPORT.md`.

## 2 minutes — run the MCP locally

Terminal A:

```bash
PYTHONPATH=src python -m ripple.mcp_server
```

Terminal B:

```bash
python scripts/mcp_smoke.py
```

The MCP target is protocol `2025-11-25` over Streamable HTTP. The server exposes five bounded tools and the Repair Card MCP App resource.

See `docs/MCP_COMPLIANCE.md` and `docs/MCP_PROTOCOL_TEST_REPORT.md` for the protocol contract.

## 2 minutes — use the simulated Alexa+ experience

```bash
PYTHONPATH=src python -m ripple.webapp
```

Open `http://127.0.0.1:8765` and keep the default utterance:

> Our flight home was cancelled. We'll land tomorrow at 18:00.

Judge the experience in this order:

1. exactly 5 affected commitments;
2. **$116 at risk → $42 repair → $74 net preserved**;
3. one exact approval CTA;
4. 0 external writes before approval;
5. five execution receipts;
6. replay deduplicates 5/5 actions while unique writes remain 5;
7. technical dependency/receipt details remain available as secondary evidence rather than dominating the decision surface.

## Generality check

The Event Operations scenario proves the engine is not flight-specific:

**$5,800 avoidable loss → $620 repair → $5,180 net preserved.**

A cheaper option is intentionally available but rejected because it preserves less net value.

## AWS Builder status

Current repository state is **AWS-ready, not AWS-live verified**. Do not score an AWS live claim that the project does not make.

Implemented evidence includes CloudFormation, Bedrock benchmark/live-verifier scripts, DynamoDB/CloudWatch adapters, IAM/Budget configuration, external-runtime credential lifecycle and post-cutover smoke/restart assertions. A live AWS claim is allowed only after `docs/AWS_LIVE_ONE_TOUCH.md` completes against a real account and the Railway public runtime passes the AWS structural smoke.

## Truthfulness / limitations

See `docs/TECHNOLOGY_DISCLOSURE.md` and the README's “What is real vs simulated” section.

The airline/ride/reservation/delivery/pet-care/calendar providers are deterministic simulations. Fixture dollar amounts are scenario values, not market statistics. No actual Alexa+ production-client session or AWS-live runtime is claimed until real evidence exists.
