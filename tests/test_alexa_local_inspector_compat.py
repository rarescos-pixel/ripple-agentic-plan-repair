from __future__ import annotations

import asyncio
import base64
import os

import httpx

from ripple.auth import reset_auth_state
from ripple.mcp_server import PROTOCOL_VERSION, SESSIONS, app

BASE = "http://testserver"
RESOURCE = f"{BASE}/mcp"


def run(coro):
    return asyncio.run(coro)


def reset():
    SESSIONS.clear()
    reset_auth_state()
    os.environ["RIPPLE_ENV"] = "test"
    os.environ["RIPPLE_PUBLIC_BASE_URL"] = BASE
    os.environ["RIPPLE_ALLOWED_ORIGINS"] = "https://judge.example"
    os.environ["RIPPLE_SERVICE_CLIENT_ID"] = "svc"
    os.environ["RIPPLE_SERVICE_CLIENT_SECRET"] = "secret"
    os.environ["RIPPLE_USER_CLIENT_ID"] = "user-client"
    os.environ["RIPPLE_USER_REDIRECT_URIS"] = "https://client.example/callback"
    os.environ["RIPPLE_DEMO_USER_PASSWORD"] = "ripple-demo-password-test"
    os.environ["RIPPLE_STATE_BACKEND"] = "memory"


async def client():
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url=BASE,
        follow_redirects=False,
    )


async def service_token(c: httpx.AsyncClient) -> str:
    basic = base64.b64encode(b"svc:secret").decode()
    response = await c.post(
        "/oauth/token",
        headers={"authorization": f"Basic {basic}"},
        data={
            "grant_type": "client_credentials",
            "scope": "mcp:service",
            "resource": RESOURCE,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_alexa_local_inspector_documented_json_only_accept_flow():
    """Amazon's Local Inspector guide documents Accept: application/json.

    The guide also shows an older client protocol version in its example. Ripple
    must accept that request shape while negotiating its required 2025-11-25
    server protocol and then allow the normal initialized/resources flow.
    """

    reset()

    async def case():
        async with await client() as c:
            token = await service_token(c)
            init = await c.post(
                "/mcp",
                headers={
                    "accept": "application/json",
                    "authorization": f"Bearer {token}",
                },
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "addon-local-inspector",
                            "version": "documented-flow",
                        },
                    },
                },
            )
            assert init.status_code == 200, init.text
            assert init.json()["result"]["protocolVersion"] == PROTOCOL_VERSION
            sid = init.headers["mcp-session-id"]

            headers = {
                "accept": "application/json",
                "authorization": f"Bearer {token}",
                "mcp-protocol-version": PROTOCOL_VERSION,
                "mcp-session-id": sid,
            }
            initialized = await c.post(
                "/mcp",
                headers=headers,
                json={"jsonrpc": "2.0", "method": "notifications/initialized"},
            )
            assert initialized.status_code == 202, initialized.text

            tools = await c.post(
                "/mcp",
                headers=headers,
                json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            )
            assert tools.status_code == 200, tools.text
            assert len(tools.json()["result"]["tools"]) == 5

            resources = await c.post(
                "/mcp",
                headers=headers,
                json={"jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {}},
            )
            assert resources.status_code == 200, resources.text
            assert resources.json()["result"]["resources"][0]["uri"].startswith("ui://ripple/")

    run(case())


def test_event_stream_only_accept_is_still_rejected():
    reset()

    async def case():
        async with await client() as c:
            token = await service_token(c)
            response = await c.post(
                "/mcp",
                headers={
                    "accept": "text/event-stream",
                    "authorization": f"Bearer {token}",
                },
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {"protocolVersion": PROTOCOL_VERSION},
                },
            )
            assert response.status_code == 406
            assert "application/json" in response.text

    run(case())
