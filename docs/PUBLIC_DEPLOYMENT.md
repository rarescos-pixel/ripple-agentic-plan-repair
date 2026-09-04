# Ripple public MCP deployment — v1.2

## Purpose
Run the same MCP/OAuth application behind a stable HTTPS URL. TLS termination may be performed by the hosting platform or reverse proxy.

## Required environment
Copy `env.example` to the host's secret/config store. Never commit real client secrets.

The critical invariant is:
`RIPPLE_PUBLIC_BASE_URL=https://host.example`
so the protected resource is exactly:
`https://host.example/mcp`.

## Public endpoints
- `GET /healthz` — unauthenticated health check.
- `GET /.well-known/oauth-protected-resource` — OAuth protected resource metadata.
- `GET /.well-known/oauth-authorization-server` — authorization server metadata.
- `GET|POST /oauth/authorize` — user consent / authorization-code endpoint with PKCE S256.
- `POST /oauth/token` — client_credentials, authorization_code and refresh_token grants.
- `POST|GET|DELETE /mcp` — MCP Streamable HTTP endpoint.

## Authentication model
- `mcp:service`: client_credentials only. Allows MCP initialization, ping, notifications and `tools/list`. It cannot call user tools.
- `mcp:tools`: authorization_code + PKCE S256. Required for every `tools/call` request.
- Client-credentials tokens are short-lived and never receive refresh tokens.
- User access tokens are short-lived; the authorization-code flow issues a refresh token.
- Bearer tokens are accepted only from the Authorization header.

## Container run
```bash
cp env.example .env
# fill real values in a secret store; .env is ignored by git

docker build -t ripple-mcp .
docker run --rm --env-file .env -p 8000:8000 ripple-mcp
```

## Validate after deployment
```bash
RIPPLE_SMOKE_BASE_URL=https://host.example \
RIPPLE_SERVICE_CLIENT_ID='...' \
RIPPLE_SERVICE_CLIENT_SECRET='...' \
RIPPLE_USER_CLIENT_ID='...' \
RIPPLE_USER_REDIRECT_URI='registered callback' \
python scripts/mcp_smoke.py
```

Expected result: authenticated initialize -> tools/list -> record_change -> preview (0 writes) -> approval (0 writes) -> execute (5 receipts) -> replay (5/5 deduplicated) -> DELETE session.

## Important current limitation
The OAuth/session stores are in-memory in v1.2. Use a single application instance for the hackathon demo. A process restart invalidates sessions/tokens. Durable AWS state is the next infrastructure milestone; do not claim restart durability yet.
