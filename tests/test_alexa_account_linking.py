from __future__ import annotations

import asyncio
import base64
import hashlib
import os
from urllib.parse import parse_qs, urlparse

import httpx

from ripple.auth import reset_auth_state
from ripple.mcp_server import app

BASE = "http://testserver"
RESOURCE = f"{BASE}/mcp"


def _run(coro):
    return asyncio.run(coro)


def _reset() -> None:
    reset_auth_state()
    os.environ["RIPPLE_ENV"] = "test"
    os.environ["RIPPLE_PUBLIC_BASE_URL"] = BASE
    os.environ["RIPPLE_SERVICE_CLIENT_ID"] = "svc"
    os.environ["RIPPLE_SERVICE_CLIENT_SECRET"] = "secret"
    os.environ["RIPPLE_USER_CLIENT_ID"] = "user-client"
    os.environ["RIPPLE_USER_REDIRECT_URIS"] = "https://alexa.example/link"
    os.environ["RIPPLE_DEMO_USER_PASSWORD"] = "ripple-demo-password-test"


async def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE, follow_redirects=False)


async def _authorize_and_get_refresh(client: httpx.AsyncClient) -> str:
    verifier = "alexa-refresh-pkce-verifier-abcdefghijklmnopqrstuvwxyz-0123456789"
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    params = {
        "response_type": "code",
        "client_id": "user-client",
        "redirect_uri": "https://alexa.example/link",
        "scope": "mcp:tools mcp:resources",
        "resource": RESOURCE,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": "alexa-state",
    }
    authorization = await client.post(
        "/oauth/authorize",
        params=params,
        data={"decision": "approve", "password": "ripple-demo-password-test"},
    )
    assert authorization.status_code == 303, authorization.text
    query = parse_qs(urlparse(authorization.headers["location"]).query)
    assert query["state"] == ["alexa-state"]
    code = query["code"][0]

    exchange = await client.post(
        "/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": "user-client",
            "redirect_uri": "https://alexa.example/link",
            "code_verifier": verifier,
            "resource": RESOURCE,
        },
    )
    assert exchange.status_code == 200, exchange.text
    assert set(exchange.json()["scope"].split()) == {"mcp:tools", "mcp:resources"}
    return exchange.json()["refresh_token"]


def test_alexa_refresh_exchange_succeeds_without_resource_parameter():
    _reset()

    async def case():
        async with await _client() as client:
            refresh = await _authorize_and_get_refresh(client)
            renewed = await client.post(
                "/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh,
                    "client_id": "user-client",
                },
            )
            assert renewed.status_code == 200, renewed.text
            body = renewed.json()
            assert body["token_type"] == "Bearer"
            assert body["expires_in"] <= 3600
            assert set(body["scope"].split()) == {"mcp:tools", "mcp:resources"}

    _run(case())


def test_refresh_rejects_an_explicit_wrong_resource():
    _reset()

    async def case():
        async with await _client() as client:
            refresh = await _authorize_and_get_refresh(client)
            rejected = await client.post(
                "/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh,
                    "client_id": "user-client",
                    "resource": "https://attacker.example/mcp",
                },
            )
            assert rejected.status_code == 400
            assert rejected.json()["error"] == "invalid_target"

    _run(case())
