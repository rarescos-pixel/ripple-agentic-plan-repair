# Open Source Mini Challenge — submission packet

## Eligibility snapshot

Ripple is a **new public open-source project created during the Amazon Developer Hackathon submission window**.

- Hackathon submission window opens: **2026-08-31**
- Repository created: **2026-09-04**
- License: **MIT** (`LICENSE`)
- Public repository: `https://github.com/rarescos-pixel/ripple-agentic-plan-repair`
- GitHub username: **rarescos-pixel**

The Open Source mini challenge is therefore entered as a **new open-source project**, not as a pre-existing project with a cosmetic README contribution.

## Required Devpost fields

### Contribution URL

Representative meaningful contribution / integration fix:

`https://github.com/rarescos-pixel/ripple-agentic-plan-repair/pull/22`

The entire repository is new during the hackathon; PR #22 is supplied as a concrete contribution URL because it demonstrates the project's open-source engineering standard rather than pointing only at a landing page.

### Project repository URL

`https://github.com/rarescos-pixel/ripple-agentic-plan-repair`

### GitHub username

`rarescos-pixel`

### What I did

I created Ripple as a new MIT-licensed Alexa+ consequence-repair project and published the complete implementation, tests, infrastructure, integration probes and judge evidence in a public GitHub repository.

The open-source work includes:

- a self-hosted MCP `2025-11-25` Streamable HTTP server;
- OAuth discovery, authorization-code + PKCE S256, service credentials and refresh-token interoperability;
- a deterministic dependency/economic repair engine;
- exact approval, bounded execution, idempotency and authoritative receipts;
- durable Memory/SQLite/DynamoDB state adapters;
- a display-only Repair Card MCP App integration;
- Alexa+ package/media validators and remote probes;
- AWS CloudFormation, Bedrock benchmark, DynamoDB/CloudWatch live-verification and least-privilege external-runtime credential lifecycle;
- adversarial tests and independent remote smoke scripts;
- real developer friction logs and evidence-bounded documentation.

### How it works

Ripple separates probabilistic language interpretation from deterministic authority:

**LLM proposes → deterministic policy validates → user approves exact plan → bounded/idempotent execution → receipts**

The repository is designed so another developer can inspect not only the happy-path implementation, but also the safety boundaries and reproducible failure evidence. Public tests pin approval drift, ambiguous provider state, hard preferences, interruption recovery, duplicate suppression and protocol interoperability.

PR #22 is one example of the open-source development pattern. While preflighting the official Alexa+ Local Inspector request sequence, the project found that the published Inspector example uses `Accept: application/json`, while Ripple's strict Streamable HTTP implementation required both JSON and SSE. The contribution:

1. reproduces the documented Inspector request shape in an integration test;
2. adds a bounded compatibility fix that still rejects SSE-only requests;
3. verifies protocol negotiation to MCP `2025-11-25`;
4. verifies tool discovery and the `ui://` Repair Card resource;
5. adds a standalone remote probe so the behavior can be checked against a deployed server;
6. records the interoperability issue in the friction log with an actionable documentation suggestion.

### Why it matters

The open-source value is larger than the demo scenario. The repository provides reusable patterns for developers building action-taking MCP systems:

- **exact approval binding** prevents a model or mutable state from silently changing what the user authorized;
- **authoritative idempotency receipts** make retries/restarts safe;
- **display-only MCP App UI** demonstrates how to add a visual decision surface without granting the UI action authority;
- **Alexa-compatible OAuth and Local Inspector probes** turn ambiguous integration details into executable interoperability tests;
- **external-PaaS AWS credential lifecycle** documents a constrained, revocable bridge when the public MCP host remains outside AWS;
- **evidence gates** distinguish a deployment status from actual functional proof.

These patterns are intentionally visible and testable so other developers can reuse or challenge them instead of relying on marketing claims.

## Open-source quality evidence

- `LICENSE` — MIT license
- `.github/workflows/quality-gate.yml` — public CI
- `tests/` — deterministic, protocol, safety, AWS lifecycle and Alexa compatibility tests
- `scripts/mcp_smoke.py` — authenticated remote MCP proof
- `scripts/alexa_local_inspector_probe.py` — documented Inspector request-shape probe
- `scripts/alexa_store_media_smoke.py` — public package/media proof
- `docs/EVIDENCE_MATRIX.md` — claim-to-evidence mapping
- `docs/FRICTION_LOG.md` — real integration friction and actionable feedback
- `docs/TECHNOLOGY_DISCLOSURE.md` — explicit real-vs-simulated boundaries

## Submission wording — compact version

**Contribution URL:** `https://github.com/rarescos-pixel/ripple-agentic-plan-repair/pull/22`  
**Repository:** `https://github.com/rarescos-pixel/ripple-agentic-plan-repair`  
**GitHub:** `rarescos-pixel`

> Ripple is a new MIT-licensed project created during the hackathon. I open-sourced the complete Alexa+ MCP consequence-repair engine, safety/approval architecture, OAuth/MCP App integration, AWS deployment tooling, adversarial tests and reproducible remote evidence. A representative contribution, PR #22, turns an Alexa Local Inspector interoperability mismatch into a tested compatibility fix and reusable remote probe. The project matters because it publishes concrete patterns for safe action-taking MCP systems—exact approval binding, replay-safe authoritative receipts, display-only MCP Apps and evidence-first interoperability checks—rather than only the hackathon demo.
