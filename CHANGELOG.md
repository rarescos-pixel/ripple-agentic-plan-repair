# Ripple Changelog

## v1.5 — Alexa-first decision surface hardening

- Repair Card now exposes a compact money summary in the judge-facing order: risk → repair cost → net value preserved;
- top consequences use human commitment labels instead of internal ids;
- visual, voice and accessibility surfaces terminate on the same exact economic approval boundary;
- the web demo now renders the canonical Repair Card and moves actions, idempotency details and snapshot hashes into secondary technical evidence;
- Event Operations now proves the same Alexa decision surface outside travel: $5,800 at risk → $620 repair → $5,180 net preserved → `Approve $620 repair`;
- these changes are additive to `ripple.repair-card.v1` and do not alter the deterministic policy, approval snapshot or execution boundary.

## v1.5 — AWS runtime cutover hardening

- added a fail-closed structural AWS runtime profile for the Railway → AWS cutover;
- production rejects partial DynamoDB / Bedrock / CloudWatch activation;
- `RIPPLE_REQUIRE_AWS_RUNTIME=true` locks the canonical deployment to the complete structural AWS profile after live provisioning;
- canonical runtime validation now occurs before state-backend construction;
- fixed Bedrock change identity: the same canonical transition is replay-stable, while genuinely different normalized changes receive different downstream idempotency identities;
- deployment map documents the controlled cutover contract;
- validation baseline after the hardening: 76/76 tests, 12/12 MCP protocol tests, 7/7 adversarial evidence scenarios, `cfn-lint` PASS, generated-evidence drift 0.

## v1.3 — pre-AWS win hardening

- planner ranks repairs by maximum net cash preserved (`avoidable_loss - added_cost`), then lower cost, reversibility, deterministic operation name;
- generic `changed_time_after_start` / `changed_time_after_end` predicates added while preserving `arrival_after_*` aliases;
- dependency traversal no longer marks a node seen before a condition actually fires;
- declarative simulated repair options enable non-flight scenarios without hard-coding planner branches;
- added event-operations economic fixture: $5,800 avoidable loss, $620 repair cost, $5,180 net preserved;
- baseline: 48 tests, 7 executable evidence scenarios;
- added cost model and pre-AWS win-hardening documents;
- candidate validated locally before promotion to `main`.

## v1.2

See repository history and release documentation for the public MCP/OAuth deployment milestone.
