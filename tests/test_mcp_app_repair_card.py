from __future__ import annotations

import asyncio
import base64
import hashlib
import os
from urllib.parse import parse_qs, urlparse

import httpx

from ripple.auth import reset_auth_state
from ripple.mcp_server import PROTOCOL_VERSION, SESSIONS, app
from ripple.presentation.mcp_app import (
    MCP_APP_MIME_TYPE,
    MCP_APP_PROTOCOL_VERSION,
    REPAIR_CARD_APP_HTML,
    REPAIR_CARD_RESOURCE_URI,
    repair_card_resource_contents,
    repair_card_resource_descriptor,
)

ACCEPT = "application/json, text/event-stream"
BASE = "http://testserver"
RESOURCE = f"{BASE}/mcp"


def run(coro):
    return asyncio.run(coro)


def reset():
    SESSIONS.clear()
    reset_auth_state()
    os.environ["RIPPLE_ENV"] = "test"
    os.environ["RIPPLE_PUBLIC_BASE_URL"] = BASE
    os.environ["RIPPLE_SERVICE_CLIENT_ID"] = "svc"
    os.environ["RIPPLE_SERVICE_CLIENT_SECRET"] = "secret"
    os.environ["RIPPLE_USER_CLIENT_ID"] = "user-client"
    os.environ["RIPPLE_USER_REDIRECT_URIS"] = "https://client.example/callback"
    os.environ["RIPPLE_DEMO_USER_PASSWORD"] = "ripple-demo-password-test"
    os.environ["RIPPLE_STATE_BACKEND"] = "memory"


async def client():
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE, follow_redirects=False)


async def service_token(c: httpx.AsyncClient) -> str:
    basic = base64.b64encode(b"svc:secret").decode()
    r = await c.post(
        "/oauth/token",
        headers={"authorization": f"Basic {basic}"},
        data={"grant_type": "client_credentials", "scope": "mcp:service", "resource": RESOURCE},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


async def user_token(c: httpx.AsyncClient) -> str:
    verifier = "ripple-app-pkce-verifier-abcdefghijklmnopqrstuvwxyz-0123456789"
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    params = {
        "response_type": "code",
        "client_id": "user-client",
        "redirect_uri": "https://client.example/callback",
        "scope": "mcp:tools",
        "resource": RESOURCE,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": "app-test",
    }
    approved = await c.post(
        "/oauth/authorize",
        params=params,
        data={"decision": "approve", "password": "ripple-demo-password-test"},
    )
    assert approved.status_code == 303, approved.text
    code = parse_qs(urlparse(approved.headers["location"]).query)["code"][0]
    token = await c.post(
        "/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": "user-client",
            "redirect_uri": "https://client.example/callback",
            "code_verifier": verifier,
            "resource": RESOURCE,
        },
    )
    assert token.status_code == 200, token.text
    return token.json()["access_token"]


async def initialize(c: httpx.AsyncClient, token: str) -> str:
    r = await c.post(
        "/mcp",
        headers={"accept": ACCEPT, "authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "mcp-app-test", "version": "1"},
            },
        },
    )
    assert r.status_code == 200, r.text
    caps = r.json()["result"]["capabilities"]
    assert caps["resources"] == {"subscribe": False, "listChanged": False}
    sid = r.headers["mcp-session-id"]
    ready = await c.post(
        "/mcp",
        headers=headers(token, sid),
        json={"jsonrpc": "2.0", "method": "notifications/initialized"},
    )
    assert ready.status_code == 202
    return sid


def headers(token: str, sid: str) -> dict[str, str]:
    return {
        "accept": ACCEPT,
        "authorization": f"Bearer {token}",
        "mcp-protocol-version": PROTOCOL_VERSION,
        "mcp-session-id": sid,
    }


async def rpc(c: httpx.AsyncClient, h: dict[str, str], req_id: int, method: str, params=None):
    return await c.post(
        "/mcp",
        headers=h,
        json={"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}},
    )


def test_resource_descriptor_and_contents_are_exact_mcp_app_contract():
    descriptor = repair_card_resource_descriptor()
    contents = repair_card_resource_contents()
    assert REPAIR_CARD_RESOURCE_URI.startswith("ui://")
    assert descriptor["uri"] == contents["uri"] == REPAIR_CARD_RESOURCE_URI
    assert descriptor["mimeType"] == contents["mimeType"] == MCP_APP_MIME_TYPE
    assert MCP_APP_MIME_TYPE == "text/html;profile=mcp-app"
    assert MCP_APP_PROTOCOL_VERSION == "2026-01-26"
    assert contents["text"] == REPAIR_CARD_APP_HTML
    assert descriptor["_meta"]["ui"]["csp"] == {"connectDomains": [], "resourceDomains": []}
    assert contents["_meta"]["ui"]["csp"] == {"connectDomains": [], "resourceDomains": []}


def test_widget_is_display_only_and_cannot_cross_approval_boundary():
    html = REPAIR_CARD_APP_HTML
    assert 'method:"ui/initialize"' in html
    assert "ui/notifications/tool-result" in html
    assert "ui/notifications/size-changed" in html
    assert "ui/resource-teardown" in html
    assert "Approve $" not in html  # exact amount only arrives from the approved preview payload
    assert "tools/call" not in html
    assert "approve_repair_plan" not in html
    assert "execute_repair_plan" not in html
    assert "fetch(" not in html
    assert "XMLHttpRequest" not in html
    assert "WebSocket" not in html
    assert "https://" not in html
    assert "http://" not in html


def test_tools_list_binds_only_preview_to_repair_card_app():
    reset()

    async def case():
        async with await client() as c:
            svc = await service_token(c)
            sid = await initialize(c, svc)
            listed = await rpc(c, headers(svc, sid), 2, "tools/list")
            assert listed.status_code == 200
            tools = {tool["name"]: tool for tool in listed.json()["result"]["tools"]}
            preview = tools["preview_repair_plan"]
            assert preview["_meta"]["ui"]["resourceUri"] == REPAIR_CARD_RESOURCE_URI
            assert preview["_meta"]["ui"]["visibility"] == ["model", "app"]
            for name in {"record_change", "approve_repair_plan", "execute_repair_plan", "get_repair_status"}:
                assert "_meta" not in tools[name]

    run(case())


def test_resources_list_and_read_return_exact_uri_mime_and_self_contained_html():
    reset()

    async def case():
        async with await client() as c:
            svc = await service_token(c)
            sid = await initialize(c, svc)
            h = headers(svc, sid)
            listed = await rpc(c, h, 2, "resources/list")
            assert listed.status_code == 200
            resources = listed.json()["result"]["resources"]
            assert len(resources) == 1
            assert resources[0]["uri"] == REPAIR_CARD_RESOURCE_URI
            assert resources[0]["mimeType"] == MCP_APP_MIME_TYPE

            read = await rpc(c, h, 3, "resources/read", {"uri": REPAIR_CARD_RESOURCE_URI})
            assert read.status_code == 200
            contents = read.json()["result"]["contents"]
            assert len(contents) == 1
            assert contents[0]["uri"] == REPAIR_CARD_RESOURCE_URI
            assert contents[0]["mimeType"] == MCP_APP_MIME_TYPE
            assert contents[0]["text"].startswith("<!doctype html>")
            assert "tools/call" not in contents[0]["text"]

            missing = await rpc(c, h, 4, "resources/read", {"uri": "ui://ripple/not-found.html"})
            assert missing.status_code == 200
            assert missing.json()["error"]["message"] == "Resource not found"

    run(case())


def test_preview_result_carries_same_ui_binding_without_changing_zero_write_semantics():
    reset()

    async def case():
        async with await client() as c:
            svc = await service_token(c)
            user = await user_token(c)
            sid = await initialize(c, svc)
            h = headers(user, sid)
            recorded = await rpc(
                c,
                h,
                3,
                "tools/call",
                {"name": "record_change", "arguments": {"utterance": "Our flight home was cancelled. We'll land tomorrow at 18:00."}},
            )
            assert recorded.status_code == 200
            preview = await rpc(c, h, 4, "tools/call", {"name": "preview_repair_plan", "arguments": {}})
            assert preview.status_code == 200
            result = preview.json()["result"]
            assert result["_meta"]["ui"]["resourceUri"] == REPAIR_CARD_RESOURCE_URI
            assert result["structuredContent"]["writes_before_approval"] == 0
            assert result["structuredContent"]["repair_card"]["decision"]["label"] == "Approve $42 repair"
            assert SESSIONS[sid].approval is None
            assert SESSIONS[sid].tools.execution_log == []

    run(case())
