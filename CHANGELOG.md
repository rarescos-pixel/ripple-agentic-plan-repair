# Changelog

## v1.2 — authenticated MCP + deployment readiness
- Replaced the mislabeled/duplicated MCP test file with 12 real MCP/OAuth protocol tests.
- Added OAuth protected-resource metadata and authorization-server metadata.
- Added client_credentials (`mcp:service`) and authorization_code + PKCE S256 (`mcp:tools`) flows.
- Added refresh tokens for the user flow and strict resource validation.
- Added scope separation: service tokens cannot call user tools.
- Added 401-without-WWW-Authenticate behavior for unauthenticated MCP requests.
- Added configurable public base URL, allowed Origins, session TTL/capacity, public health endpoint.
- Added Dockerfile, `.dockerignore`, `env.example`, authenticated real-HTTP smoke client, and public deployment runbook.
- Full suite: 43/43 PASS; authenticated MCP/OAuth suite: 12/12 PASS; release gate PASS.
- Real TCP/HTTP authenticated smoke: PASS.
- Public Railway MCP deployment and independent remote authenticated smoke: PASS.
- Public repository synchronized with full tests, judge packet and reproducible CI.

## v0.2 — 2026-09-02
- Implemented executable golden vertical slice.
- Added deterministic dependency traversal and repair planning.
- Added five simulated service adapters.
- Added exact-plan approval gate and cost ceiling.
- Added idempotent replay protection.
- Added truthful partial-failure behavior.
- Added golden and safety tests.

## v0.1 — 2026-09-02
- Locked consequence-aware plan repair concept and canonical schema.

## v0.3 — local agent boundary + judge evidence
- Added pluggable natural-language ChangeInterpreter boundary.
- Added RippleAgent and two-phase RippleSession (propose -> approve -> execute).
- Added executable CLI demo.
- Added quantified rubric-evidence collector.
- Added architecture, rubric mapping, and evaluation documents.
- Preserved deterministic approval/idempotency guarantees around all writes.

## v0.4 — deterministic dependency predicates
- Added deterministic edge conditions for time-dependent impact detection.
- Added negative test proving unaffected commitments are not repaired.
- Added two-step dependency traversal test through a non-actionable fact node.
- Removed the golden fixture shortcut that marked every downstream node impacted.

## v0.5 — adversarial scenario matrix
- Added exact content-hash binding to approvals; same-version plan drift now requires re-approval.
- Added unresolved-impact behavior for missed repair deadlines.
- Added whole-plan provider ambiguity preflight with zero-write guarantee.
- Added hard user-operation constraints before cost optimization.
- Added persisted in-memory receipt log and simulated interruption recovery.
- Added five adversarial scenario tests covering deadline, ambiguity, preference, drift, and recovery.

## v0.6 — executable evidence matrix
- Added a judge-facing executable scenario matrix instead of relying on prose claims.
- Added quantified evidence for golden value, missed deadlines, provider ambiguity, hard preferences, content drift, and interruption recovery.
- Added reproducible generation of `docs/EVIDENCE_MATRIX.md`.

## v0.7 — Bedrock integration contract + cost gate
- Added injectable Bedrock/Nova 2 Lite ChangeInterpreter contract using forced client-side `record_change` tool calling.
- Added canonical node/field validation and confidence threshold before planning.
- Authoritative old values remain application-owned; model output cannot overwrite them.
- Added one-call input/output model budget and tests that block oversized prompts before inference.
- Added minimal four-service AWS readiness plan and explicit no-feature-bloat exclusions.

## v0.8
- Added zero-cloud Alexa+ web simulation with proposal/approval/execution/replay UX.
- Added controller tests proving zero writes before approval and replay idempotency.
- Recorded prior 32-minute Work run as UNRECONCILED rather than discarding or trusting it.
- Work credits are no longer a blocker for local MVP development.

## v1.0 — local MVP freeze candidate
- Added GitHub Actions quality gate for tests and executable-evidence drift detection.
- Added clean-room reproduction instructions.
- Prepared the package for clean extraction and validation without hidden workspace state.
- Freeze cleanup: restored `.gitignore`, full MIT license text, and a human-readable golden fixture bound to an executable contract test.

## v1.1.0 — MCP + exact-approval P0 fixes
- Fixed web approval TOCTOU: client-visible snapshot is now echoed and validated server-side.
- Fixed deterministic demo time normalization: user's actual HH:MM controls the ChangeEvent.
- Expanded snapshot hash to include impacts/options.
- Added real stateful MCP Streamable HTTP endpoint `/mcp` for protocol 2025-11-25.
- Added five bounded MCP tools and protocol conformance tests.
- Added Origin, Accept, protocol-version and session validation.
- Protocol/security follow-up: terminated sessions now return HTTP 404; Origin validation rejects hostname-prefix rebinding tricks; full suite 36/36 PASS.
