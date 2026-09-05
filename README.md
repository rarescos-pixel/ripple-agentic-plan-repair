# Ripple

[![Ripple quality gate](https://github.com/rarescos-pixel/ripple-agentic-plan-repair/actions/workflows/quality-gate.yml/badge.svg)](https://github.com/rarescos-pixel/ripple-agentic-plan-repair/actions/workflows/quality-gate.yml)

## Tell Alexa one thing that changed. Ripple fixes what breaks downstream.

> **“Our flight home was cancelled. We’ll land tomorrow at six.”**
>
> **5 commitments affected · $116 at risk · $42 repair cost · $74 net cash preserved**
>
> **Approve $42 repair?**

Ripple is a **money-aware consequence-repair layer for Alexa+**. A single real-world change can invalidate a ride, reservation, delivery, care booking, calendar event, or other dependent commitment. Ripple finds the cascade, quantifies what is at risk, chooses the repair that preserves the most net value, asks for one exact approval, then executes safely and returns receipts.

This is not a generic Q&A wrapper. The core primitive is:

**change → dependency analysis → consequences → economic exposure → optimized repair → exact approval → bounded execution → durable receipts**

## Why Alexa+

Disruptions are divided-attention moments. The user should not have to discover five broken plans across five apps while already handling the original problem. Voice is the fastest way to state the changed fact; the Repair Card makes the consequence set, money and approval boundary visible at a glance.

Ripple keeps voice and screen aligned:

- the spoken summary and visual card expose the same money totals;
- the call to action is the same exact approval, for example **“Approve $42 repair”**;
- material drift in cost, scope, snapshot or notifications invalidates approval and forces re-approval;
- the MCP App is display-only and cannot approve or execute actions itself.

## Golden demo

One changed arrival time produces five downstream impacts:

| Outcome | Verified fixture value |
|---|---:|
| Commitments affected | **5** |
| Direct avoidable loss | **$116** |
| Repair cost | **$42** |
| Net direct cash preserved | **$74** |
| Writes before approval | **0** |
| Writes during approval | **0** |
| Authoritative execution receipts | **5** |
| Exact-plan replay | **5/5 deduplicated** |

The public authenticated MCP flow has been exercised from a separate Railway container over HTTPS. See [`docs/REMOTE_SMOKE_REPORT.md`](docs/REMOTE_SMOKE_REPORT.md) and [`docs/ALEXA_REMOTE_EVIDENCE.md`](docs/ALEXA_REMOTE_EVIDENCE.md).

## A second scenario proves the engine is not travel-specific

**Event Operations Cascade** models a conference-time change across AV delivery, catering, VIP transport, security staffing and a sponsor briefing.

- **$5,800** avoidable loss
- **$620** repair cost
- **$5,180** net cash preserved

The planner intentionally receives a cheaper option that saves less money. Ripple selects the option with the highest **avoidable loss − repair cost**, then applies deterministic tie-breakers. The language model does not choose the economic repair.

## Safety architecture

Ripple uses a deliberately narrow authority model:

**LLM proposes → deterministic policy validates → user approves exact plan → bounded/idempotent execution → receipts**

Key invariants:

- the LLM never receives write authority;
- the LLM does not decide which repair spends money;
- preview and approval phases perform zero provider writes;
- approval binds to plan ID, version, exact snapshot content, maximum cost and notification scope;
- ambiguous provider state fails closed before execution;
- every external action has an idempotency key;
- authoritative receipts prevent duplicate writes on replay or restart;
- unresolved work stays visible rather than being reported as success.

The deterministic release gate is **PASS** and includes golden, failure, drift, preference, economic-choice and interruption-recovery scenarios. See [`docs/VALIDATION_REPORT.md`](docs/VALIDATION_REPORT.md).

## Alexa+ / MCP implementation

Public runtime:

- HTTPS: `https://ripple-v12-production.up.railway.app`
- MCP: `https://ripple-v12-production.up.railway.app/mcp`
- base protocol: **MCP 2025-11-25**, Streamable HTTP

Implemented surfaces include:

- stateful MCP sessions and protocol-version enforcement;
- OAuth protected-resource and authorization-server discovery;
- service client credentials plus authorization-code + PKCE S256 user flow;
- Alexa-compatible refresh-token behavior while rejecting an explicitly wrong resource;
- five bounded MCP tools: `record_change`, `preview_repair_plan`, `approve_repair_plan`, `execute_repair_plan`, `get_repair_status`;
- a real MCP App Repair Card exposed through `ui://` resources with `text/html;profile=mcp-app`;
- Alexa+ add-on package assets, six required icon sizes, 600×900 carousel, privacy and terms surfaces;
- independent remote gates for authenticated execution, replay and store-media packaging.

Observed public smoke contract:

```text
Ripple authenticated MCP smoke: PASS
protocol: 2025-11-25
preview: 5 impacts / 0 writes
approval writes: 0
execute: 5 receipts / 5 unique writes
replay: 5 deduplicated / 5 unique writes
```

## AWS Builder architecture

Ripple keeps Railway as the public MCP transport host. AWS is designed to be **structural rather than decorative**:

- **Amazon Bedrock** — natural-language change normalization only;
- **Amazon DynamoDB** — durable exact approvals, idempotency records and authoritative receipts;
- **Amazon CloudWatch Logs** — redacted structured runtime traces;
- **IAM** — resource-scoped runtime permissions;
- **AWS Budgets** — project cost guardrails.

The CloudFormation, runtime adapters, live benchmark harness, least-privilege policy, budget, credential-lifecycle scripts and cutover gates are implemented and CI-validated. **AWS is currently AWS-ready, not AWS-live verified.** Ripple will not claim live Bedrock/DynamoDB/CloudWatch use until the real stack is provisioned, exercised and the public Railway runtime passes the post-cutover smoke and restart/replay proof on one source SHA.

See [`docs/AWS_READY_V15.md`](docs/AWS_READY_V15.md), [`docs/AWS_RUNTIME_CREDENTIALS.md`](docs/AWS_RUNTIME_CREDENTIALS.md) and [`docs/AWS_LIVE_ONE_TOUCH.md`](docs/AWS_LIVE_ONE_TOUCH.md).

## What is real vs simulated

Real running software:

- public HTTPS MCP transport;
- OAuth and PKCE surfaces;
- dependency analysis and economic optimization;
- exact approval boundary;
- execution ledger, receipts and duplicate-free replay;
- MCP App Repair Card and Alexa package/media surfaces;
- independent remote smoke/evidence runners.

Deliberately simulated today:

- airline, ride, reservation, delivery, pet-care and calendar provider adapters;
- the example dollar amounts, which are deterministic scenario fixtures rather than market claims;
- an actual Alexa+ production-client session has not yet been claimed;
- AWS live runtime is not claimed until the live gate passes.

This distinction is intentional: marketing copy does not count as evidence.

## Judge evidence map

- [`docs/ALEXA_REMOTE_EVIDENCE.md`](docs/ALEXA_REMOTE_EVIDENCE.md) — remote Alexa-compatible OAuth, MCP and store-media evidence
- [`docs/MCP_APP_EVIDENCE.md`](docs/MCP_APP_EVIDENCE.md) — Repair Card MCP App contract
- [`docs/REMOTE_SMOKE_REPORT.md`](docs/REMOTE_SMOKE_REPORT.md) — independent public HTTPS execution/replay proof
- [`docs/VALIDATION_REPORT.md`](docs/VALIDATION_REPORT.md) — deterministic release gate
- [`docs/EVIDENCE_MATRIX.md`](docs/EVIDENCE_MATRIX.md) — claim-to-evidence mapping
- [`docs/RUBRIC_MAP.md`](docs/RUBRIC_MAP.md) — judging-criterion mapping
- [`docs/FRICTION_LOG.md`](docs/FRICTION_LOG.md) — real developer friction and actionable Amazon feedback
- [`docs/COST_MODEL.md`](docs/COST_MODEL.md) — measured/runtime cost model and cost-efficiency decisions

## Run locally

```bash
python -m pip install -e .
PYTHONPATH=src python -m ripple.mcp_server
```

Local MCP endpoint: `http://127.0.0.1:8000/mcp`.

Run the test suite:

```bash
PYTHONPATH=src python -m pytest -q
```

The repository quality gate also validates MCP protocol conformance, the Repair Card MCP App safety contract, Alexa+ package requirements, CloudFormation, AWS live/credential lifecycle scripts, generated evidence and documentation coherence.

## License

Released under the **MIT License**. See [`LICENSE`](LICENSE).
