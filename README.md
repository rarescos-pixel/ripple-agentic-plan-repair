# Ripple

**v1.2 — Alexa+ remote-readiness milestone**

**Tell Alexa one thing that changed. Ripple fixes what breaks downstream.**

Ripple is a consequence-aware plan repair agent for the Amazon Developer Hackathon. One changed fact is propagated through a dependency graph into a bounded repair plan across heterogeneous commitments.

## Current milestone — v1.2 authenticated MCP + deployment freeze
The local MVP includes deterministic dependency predicates, exact-content approval, provider-ambiguity preflight, hard preference constraints, truthful unresolved/failure states, idempotent replay, interruption recovery, a constrained Bedrock adapter boundary, a judge-facing simulated Alexa+ web experience, a real MCP Streamable HTTP server, OAuth 2.1 discovery/authentication surfaces, container deployment assets, and a reproducible release gate.

AWS remains intentionally deferred until cloud access is worth the marginal cost. No live AWS/Alexa+ client or real airline/ride/reservation/delivery/care/payment integration is claimed. The local `/mcp` server itself is real and protocol-tested.

## Validate
```bash
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m ripple.evaluation.matrix
PYTHONPATH=src python -m ripple.evaluation.release_gate
```

Current freeze expectation: **43 tests PASS**, including **12 authenticated MCP/OAuth protocol tests**; **6/6 adversarial scenarios PASS**; release gate **PASS**.

## Local CLI demo
```bash
PYTHONPATH=src python -m ripple.demo
```

## Simulated Alexa+ web experience
```bash
PYTHONPATH=src python -m ripple.webapp
```
Open `http://127.0.0.1:8765`.

The judge-facing demo shows:
- five downstream dependency paths;
- $42 recovery cost / $116 direct loss avoided / $74 net direct cash preserved;
- zero external writes before approval;
- exact approval scope and plan snapshot hash;
- five authoritative execution receipts;
- 5/5 deduplication on exact-plan replay;
- the 6/6 executable adversarial evidence matrix.

## Judge / submission documents
- `docs/JUDGE_RUNBOOK.md`
- `docs/VALIDATION_REPORT.md`
- `docs/EVIDENCE_MATRIX.md`
- `docs/VIDEO_SCRIPT.md`
- `docs/SUBMISSION_DRAFT.md`
- `docs/TECHNOLOGY_DISCLOSURE.md`
- `docs/RELEASE_CHECKLIST.md`

## Architecture and state
- `docs/MASTER.md` — canonical product/safety state
- `docs/ARCHITECTURE.md` — trust boundary and target AWS architecture
- `docs/AWS_READINESS.md` — minimal cost-efficient AWS plan
- `fixtures/golden_scenario.json` — human-readable golden contract

## CI / clean-room
The future public repo is pre-wired with `.github/workflows/quality-gate.yml`. See `docs/CLEAN_ROOM.md` for clean-room reproduction.

## Core invariant
**LLM proposes → deterministic policy validates → user approves the exact plan snapshot → bounded idempotent tools execute → receipts are authoritative.**


## MCP server (2025-11-25)
Run locally:
```bash
PYTHONPATH=src python -m ripple.mcp_server
```
Endpoint: `http://127.0.0.1:8000/mcp`. The server implements stateful Streamable HTTP initialization, `MCP-Session-Id`, `tools/list`, `tools/call`, Origin validation, protocol-version enforcement, exact approval and replay-safe execution. See `docs/MCP_COMPLIANCE.md`.

### P0 safety fixes in v1.1
- Web approval now echoes and validates the exact snapshot displayed to the user; the server no longer regenerates approval from current mutable state.
- The deterministic demo interpreter parses the actual HH:MM stated by the user. Changing 18:00 to 23:55 changes the canonical event and plan snapshot.
- Approval snapshot hashing now includes judge-visible Impact content as well as actions/totals/scope.


## Alexa+ remote-readiness
Ripple v1.2 adds the authentication/discovery surfaces required by the current Alexa+ MCP onboarding guidance:
- `/.well-known/oauth-protected-resource`;
- `/.well-known/oauth-authorization-server`;
- OAuth client-credentials for `mcp:service`;
- OAuth authorization-code + PKCE S256 for `mcp:tools`;
- refresh-token issuance for the demo user flow;
- 401 without `WWW-Authenticate` for unauthenticated MCP requests;
- scope separation: service tokens can initialize/list tools but cannot execute user tools.

Run the authenticated real-HTTP smoke test with `python scripts/mcp_smoke.py`. See `docs/PUBLIC_DEPLOYMENT.md`.
