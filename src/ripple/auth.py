from __future__ import annotations

import base64
import hashlib
import html
import os
import secrets
import time
from dataclasses import dataclass
from typing import Dict, Iterable
from urllib.parse import urlencode, parse_qs

from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, Response


@dataclass(frozen=True)
class AuthConfig:
    public_base_url: str
    service_client_id: str
    service_client_secret: str
    user_client_id: str
    user_redirect_uris: tuple[str, ...]
    demo_user_password: str
    environment: str = "development"
    token_ttl_seconds: int = 3600
    auth_code_ttl_seconds: int = 300
    refresh_ttl_seconds: int = 2_592_000

    @property
    def resource(self) -> str:
        return f"{self.public_base_url.rstrip('/')}/mcp"

    @property
    def issuer(self) -> str:
        return self.public_base_url.rstrip('/')


def load_auth_config() -> AuthConfig:
    base = os.getenv("RIPPLE_PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    redirects = tuple(
        x.strip() for x in os.getenv("RIPPLE_USER_REDIRECT_URIS", "http://127.0.0.1:9999/callback").split(",") if x.strip()
    )
    config = AuthConfig(
        public_base_url=base,
        service_client_id=os.getenv("RIPPLE_SERVICE_CLIENT_ID", "ripple-service-test"),
        service_client_secret=os.getenv("RIPPLE_SERVICE_CLIENT_SECRET", "ripple-service-secret-test"),
        user_client_id=os.getenv("RIPPLE_USER_CLIENT_ID", "ripple-user-test"),
        user_redirect_uris=redirects,
        demo_user_password=os.getenv("RIPPLE_DEMO_USER_PASSWORD", "ripple-demo-password-test"),
        environment=os.getenv("RIPPLE_ENV", "development").lower(),
    )
    validate_auth_config(config)
    return config


def validate_auth_config(c: AuthConfig) -> None:
    if c.environment not in {"development", "test", "production"}:
        raise RuntimeError("RIPPLE_ENV must be development, test, or production")
    if c.environment == "production":
        if not c.public_base_url.startswith("https://"):
            raise RuntimeError("Production RIPPLE_PUBLIC_BASE_URL must use HTTPS")
        if c.service_client_secret == "ripple-service-secret-test" or len(c.service_client_secret) < 24:
            raise RuntimeError("Production service client secret is missing or too weak")
        if c.demo_user_password == "ripple-demo-password-test" or len(c.demo_user_password) < 12:
            raise RuntimeError("Production demo user password is missing or too weak")
        if not c.user_redirect_uris or any(not uri.startswith("https://") for uri in c.user_redirect_uris):
            raise RuntimeError("Production user redirect URIs must use HTTPS")


@dataclass
class TokenRecord:
    token: str
    client_id: str
    scopes: frozenset[str]
    resource: str
    subject: str | None
    expires_at: float
    token_type: str = "access"

    def active(self) -> bool:
        return time.time() < self.expires_at


@dataclass
class AuthorizationCode:
    code: str
    client_id: str
    redirect_uri: str
    resource: str
    scopes: frozenset[str]
    code_challenge: str
    subject: str
    expires_at: float


ACCESS_TOKENS: Dict[str, TokenRecord] = {}
REFRESH_TOKENS: Dict[str, TokenRecord] = {}
AUTH_CODES: Dict[str, AuthorizationCode] = {}


def reset_auth_state() -> None:
    ACCESS_TOKENS.clear()
    REFRESH_TOKENS.clear()
    AUTH_CODES.clear()


def _oauth_error(error: str, description: str, status: int = 400) -> JSONResponse:
    return JSONResponse({"error": error, "error_description": description}, status_code=status)


def _parse_basic(value: str | None) -> tuple[str, str] | None:
    if not value or not value.lower().startswith("basic "):
        return None
    try:
        raw = base64.b64decode(value.split(" ", 1)[1]).decode("utf-8")
        client_id, secret = raw.split(":", 1)
        return client_id, secret
    except Exception:
        return None


def _scope_set(raw: str | None) -> frozenset[str]:
    return frozenset(x for x in (raw or "").split() if x)


def _issue_access(config: AuthConfig, client_id: str, scopes: Iterable[str], *, subject: str | None) -> TokenRecord:
    token = secrets.token_urlsafe(32)
    rec = TokenRecord(token, client_id, frozenset(scopes), config.resource, subject, time.time() + config.token_ttl_seconds)
    ACCESS_TOKENS[token] = rec
    return rec


def _issue_refresh(config: AuthConfig, client_id: str, scopes: Iterable[str], *, subject: str) -> TokenRecord:
    token = secrets.token_urlsafe(36)
    rec = TokenRecord(token, client_id, frozenset(scopes), config.resource, subject, time.time() + config.refresh_ttl_seconds, token_type="refresh")
    REFRESH_TOKENS[token] = rec
    return rec


def _pkce_s256(verifier: str) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")


def authenticate_request(request: Request, required_scopes: Iterable[str]) -> TokenRecord | None:
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    rec = ACCESS_TOKENS.get(token)
    if not rec or not rec.active():
        return None
    config = load_auth_config()
    if rec.resource != config.resource:
        return None
    required = set(required_scopes)
    if not required.issubset(rec.scopes):
        return None
    return rec


async def protected_resource_metadata(request: Request) -> Response:
    c = load_auth_config()
    return JSONResponse({
        "resource": c.resource,
        "authorization_servers": [c.issuer],
        "scopes_supported": ["mcp:service", "mcp:tools", "mcp:resources"],
        "bearer_methods_supported": ["header"],
    })


async def authorization_server_metadata(request: Request) -> Response:
    c = load_auth_config()
    return JSONResponse({
        "issuer": c.issuer,
        "authorization_endpoint": f"{c.issuer}/oauth/authorize",
        "token_endpoint": f"{c.issuer}/oauth/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["client_credentials", "authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["mcp:service", "mcp:tools", "mcp:resources"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic", "none"],
    })


async def authorize(request: Request) -> Response:
    c = load_auth_config()
    q = request.query_params
    client_id = q.get("client_id")
    redirect_uri = q.get("redirect_uri")
    response_type = q.get("response_type")
    resource = q.get("resource")
    code_challenge = q.get("code_challenge")
    method = q.get("code_challenge_method")
    state = q.get("state")
    scopes = _scope_set(q.get("scope")) or frozenset({"mcp:tools"})
    if client_id != c.user_client_id:
        return _oauth_error("unauthorized_client", "Unknown user client", 401)
    if redirect_uri not in c.user_redirect_uris:
        return _oauth_error("invalid_request", "redirect_uri is not registered")
    if response_type != "code":
        return _oauth_error("unsupported_response_type", "Only response_type=code is supported")
    if resource != c.resource:
        return _oauth_error("invalid_target", "resource must match the canonical MCP URI")
    if method != "S256" or not code_challenge:
        return _oauth_error("invalid_request", "PKCE S256 is required")
    if not scopes.issubset({"mcp:tools", "mcp:resources"}):
        return _oauth_error("invalid_scope", "Only user-level MCP scopes are permitted")

    if request.method == "POST":
        raw = (await request.body()).decode("utf-8")
        form = {k: v[-1] for k, v in parse_qs(raw, keep_blank_values=True).items()}
        if form.get("decision") != "approve":
            params = {"error": "access_denied"}
            if state: params["state"] = state
            return RedirectResponse(f"{redirect_uri}?{urlencode(params)}", status_code=303)
        if not secrets.compare_digest(str(form.get("password", "")), c.demo_user_password):
            params = {"error": "access_denied", "error_description": "Demo user authentication failed"}
            if state: params["state"] = state
            return RedirectResponse(f"{redirect_uri}?{urlencode(params)}", status_code=303)
        code = secrets.token_urlsafe(28)
        AUTH_CODES[code] = AuthorizationCode(
            code, client_id, redirect_uri, resource, scopes, code_challenge,
            subject="demo-user", expires_at=time.time() + c.auth_code_ttl_seconds,
        )
        params = {"code": code}
        if state: params["state"] = state
        return RedirectResponse(f"{redirect_uri}?{urlencode(params)}", status_code=303)

    hidden = "".join(
        f'<input type="hidden" name="{html.escape(k)}" value="{html.escape(v)}">'
        for k, v in q.multi_items()
    )
    return HTMLResponse(f"""<!doctype html><html><head><title>Ripple account linking</title></head>
<body><main><h1>Connect Ripple</h1><p>Allow Alexa+ to preview and execute plan repairs on your behalf?</p>
<form method="post" action="/oauth/authorize?{html.escape(str(request.url.query))}">{hidden}
<label>Demo account password <input type="password" name="password" autocomplete="current-password" required></label><br>
<button name="decision" value="approve" type="submit">Approve</button>
<button name="decision" value="deny" type="submit">Deny</button></form></main></body></html>""")


async def token(request: Request) -> Response:
    c = load_auth_config()
    raw = (await request.body()).decode("utf-8")
    form = {k: v[-1] for k, v in parse_qs(raw, keep_blank_values=True).items()}
    grant_type = str(form.get("grant_type", ""))
    resource = str(form.get("resource", ""))
    if resource != c.resource:
        return _oauth_error("invalid_target", "resource must match the canonical MCP URI")

    if grant_type == "client_credentials":
        creds = _parse_basic(request.headers.get("authorization"))
        if creds != (c.service_client_id, c.service_client_secret):
            return _oauth_error("invalid_client", "Service client authentication failed", 401)
        scopes = _scope_set(str(form.get("scope", ""))) or frozenset({"mcp:service"})
        if scopes != frozenset({"mcp:service"}):
            return _oauth_error("invalid_scope", "client_credentials may request only mcp:service")
        access = _issue_access(c, c.service_client_id, scopes, subject=None)
        return JSONResponse({"access_token": access.token, "token_type": "Bearer", "expires_in": c.token_ttl_seconds, "scope": "mcp:service"})

    if grant_type == "authorization_code":
        code = str(form.get("code", ""))
        rec = AUTH_CODES.pop(code, None)
        if not rec or time.time() >= rec.expires_at:
            return _oauth_error("invalid_grant", "Authorization code is invalid or expired")
        if str(form.get("client_id", "")) != rec.client_id or str(form.get("redirect_uri", "")) != rec.redirect_uri:
            return _oauth_error("invalid_grant", "Client or redirect mismatch")
        verifier = str(form.get("code_verifier", ""))
        if not verifier or not secrets.compare_digest(_pkce_s256(verifier), rec.code_challenge):
            return _oauth_error("invalid_grant", "PKCE verification failed")
        access = _issue_access(c, rec.client_id, rec.scopes, subject=rec.subject)
        refresh = _issue_refresh(c, rec.client_id, rec.scopes, subject=rec.subject)
        return JSONResponse({
            "access_token": access.token, "token_type": "Bearer", "expires_in": c.token_ttl_seconds,
            "refresh_token": refresh.token, "scope": " ".join(sorted(rec.scopes)),
        })

    if grant_type == "refresh_token":
        refresh_token = str(form.get("refresh_token", ""))
        rec = REFRESH_TOKENS.get(refresh_token)
        if not rec or not rec.active():
            return _oauth_error("invalid_grant", "Refresh token is invalid or expired")
        if str(form.get("client_id", "")) != rec.client_id:
            return _oauth_error("invalid_client", "Client mismatch", 401)
        access = _issue_access(c, rec.client_id, rec.scopes, subject=rec.subject)
        return JSONResponse({
            "access_token": access.token, "token_type": "Bearer", "expires_in": c.token_ttl_seconds,
            "scope": " ".join(sorted(rec.scopes)),
        })

    return _oauth_error("unsupported_grant_type", "Unsupported grant_type")
