# Ripple Changelog

## v1.3 — pre-AWS win hardening

- planner ranks repairs by maximum net cash preserved (`avoidable_loss - added_cost`), then lower cost, reversibility, deterministic operation name;
- generic `changed_time_after_start` / `changed_time_after_end` predicates added while preserving `arrival_after_*` aliases;
- dependency traversal no longer marks a node seen before a condition actually fires;
- declarative simulated repair options enable non-flight scenarios without hard-coding planner branches;
- added event-operations economic fixture: $5,800 avoidable loss, $620 repair cost, $5,180 net preserved;
- baseline: 48 tests, 7 executable evidence scenarios;
- added cost model and pre-AWS win-hardening documents.

## v1.2

See repository history and release documentation for the public MCP/OAuth deployment milestone.
