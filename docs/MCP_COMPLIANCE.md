# MCP + Alexa+ remote-readiness — 2025-11-25

Ripple v1.2 exposes a real MCP endpoint at `/mcp` and a self-contained hackathon OAuth surface.

## MCP Streamable HTTP
- POST `/mcp` for JSON-RPC requests/notifications.
- GET `/mcp` returns 405 because this server does not initiate server-to-client SSE.
- DELETE `/mcp` terminates a stateful session.
- `initialize` negotiates protocol version `2025-11-25` and returns a cryptographically random `MCP-Session-Id`.
- `notifications/initialized` gates normal operation.
- `MCP-Protocol-Version: 2025-11-25` is required after initialization.
- POST `Accept` must include both `application/json` and `text/event-stream`.
- Incoming `Origin` is exact-allowlist validated (localhost is allowed for local development).
- Server declares the `tools` capability and implements `tools/list` and `tools/call`.

## OAuth discovery/authentication
- `/.well-known/oauth-protected-resource` returns the canonical MCP resource and authorization server.
- `/.well-known/oauth-authorization-server` advertises client_credentials, authorization_code, refresh_token and PKCE S256.
- Unauthenticated `/mcp` requests return HTTP 401 without `WWW-Authenticate`.
- `mcp:service` is issued only through client_credentials and cannot call user tools.
- `mcp:tools` is issued through authorization_code + PKCE S256 and is required for all `tools/call` requests.
- The authorization-code flow issues a refresh token; client_credentials never does.
- Every token request validates the `resource` parameter against the canonical MCP URI.
- Bearer tokens are accepted only in the Authorization header.

## Ripple tools
1. `record_change`
2. `preview_repair_plan`
3. `approve_repair_plan`
4. `execute_repair_plan`
5. `get_repair_status`

## Safety boundary
`approve_repair_plan` validates the exact client-visible plan id, version, snapshot hash, maximum cost and notification scope. It records approval but performs zero writes. `execute_repair_plan` cannot run without that accepted approval. Replay uses the same approval and is idempotent.

## Tests
`tests/test_mcp_protocol_2025_11_25.py` contains 12 actual ASGI protocol/authentication tests. The previous v1.1 package accidentally contained duplicate web tests under this filename; v1.2 explicitly corrects that packaging defect.

Coverage includes:
- discovery metadata;
- unauthenticated 401 behavior;
- client-credentials service scope;
- authorization-code + PKCE S256;
- bad verifier rejection;
- refresh token;
- service/user scope separation;
- initialize/session/tool discovery;
- full user tool flow and idempotent replay;
- Origin validation;
- authenticated GET/405 behavior;
- session termination;
- health endpoint.

A separate TCP/HTTP smoke client (`scripts/mcp_smoke.py`) runs the complete authenticated flow against a real Uvicorn process.

## Current limitation
The bundled OAuth/token/session stores are in-memory. This is appropriate for the single-instance hackathon demo but is not presented as production identity infrastructure or restart-durable state. The public deployment should stay single-instance until durable state or a managed identity provider is introduced.

## Official references
- https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
- https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-quickstart.html
- https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-authentication.html
- https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-account-linking.html
