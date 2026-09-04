# Ripple — MCP/OAuth Protocol Test Report v1.2

## Target
MCP Streamable HTTP protocol `2025-11-25` plus the OAuth surfaces used by the remote Alexa+ integration path.

## Local conformance result
- full project suite: **43/43 PASS**;
- MCP/OAuth module: **12/12 PASS**;
- adversarial matrix: **6/6 PASS**;
- deterministic release gate: **PASS**.

Coverage includes discovery metadata, unauthenticated 401 behavior, service/user scope separation, client credentials, authorization-code + PKCE S256, bad-verifier rejection, refresh token, initialize/session lifecycle, `tools/list`, full user tool flow, Origin validation, GET/405 behavior, session DELETE and health/readiness.

## Public remote proof
A second Railway container called `https://ripple-v12-production.up.railway.app` over public HTTPS and reported `Ripple authenticated MCP smoke: PASS`.

Observed semantic assertions:
- protocol `2025-11-25`;
- five expected tools;
- preview 5 impacts / 0 writes;
- approval 0 writes;
- execute 5 receipts / 5 unique writes;
- replay 5 deduplicated / still 5 unique writes;
- session termination 204.

Server-side Railway logs independently corroborated the same OAuth and MCP requests. See `docs/REMOTE_SMOKE_REPORT.md`.

These are project-owned conformance tests derived from the official MCP requirements; they are not represented as the upstream SDK repository's own test suite.
