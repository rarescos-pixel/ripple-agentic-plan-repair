# Ripple — P0 Fix Report v1.2

## P0-1: exact approval TOCTOU
The client now echoes the exact snapshot shown to the user; deterministic policy checks plan id, version, complete content hash, cost ceiling and notification scope against authoritative state before any write. Server-side drift after display produces zero writes.

## P0-2: stated time ignored by demo interpreter
The deterministic demo parser now binds the actual stated `HH:MM` to the canonical ChangeEvent. `18:00` and `23:55` produce different changes and approval snapshots. It remains intentionally narrow and is not presented as general NLP.

## Additional hardening
- snapshot hash includes judge-visible impacts/options as well as actions/totals/scope;
- provider ambiguity is preflight-blocked before the first write;
- replay and interrupted recovery are idempotent;
- OAuth/MCP scope separation keeps service discovery credentials out of user tool authority.

## Verified result
- **43/43** full tests PASS;
- **12/12** MCP/OAuth tests PASS;
- **6/6** adversarial scenarios PASS;
- release gate PASS;
- independent public remote MCP smoke PASS.
