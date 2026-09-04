from __future__ import annotations

import asyncio
import base64
import hashlib
import os
from urllib.parse import parse_qs, urlparse

import httpx

from ripple.auth import reset_auth_state
from ripple.mcp_server import PROTOCOL_VERSION, SESSIONS, app

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
    os.environ["RIPPLE_ALLOWED_ORIGINS"] = "https://judge.example"
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
    r = await c.post("/oauth/token", headers={"authorization": f"Basic {basic}"}, data={
        "grant_type": "client_credentials", "scope": "mcp:service", "resource": RESOURCE,
    })
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


async def user_token(c: httpx.AsyncClient) -> tuple[str, str]:
    verifier = "ripple-pkce-verifier-abcdefghijklmnopqrstuvwxyz-0123456789"
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    params = {
        "response_type": "code", "client_id": "user-client",
        "redirect_uri": "https://client.example/callback", "scope": "mcp:tools",
        "resource": RESOURCE, "code_challenge": challenge, "code_challenge_method": "S256", "state": "abc",
    }
    r = await c.post("/oauth/authorize", params=params, data={"decision": "approve", "password": "ripple-demo-password-test"})
    assert r.status_code == 303, r.text
    q = parse_qs(urlparse(r.headers["location"]).query)
    code = q["code"][0]
    assert q["state"][0] == "abc"
    t = await c.post("/oauth/token", data={
        "grant_type": "authorization_code", "code": code, "client_id": "user-client",
        "redirect_uri": "https://client.example/callback", "code_verifier": verifier, "resource": RESOURCE,
    })
    assert t.status_code == 200, t.text
    body = t.json()
    return body["access_token"], body["refresh_token"]


async def initialize(c: httpx.AsyncClient, bearer: str) -> str:
    r = await c.post("/mcp", headers={"accept": ACCEPT, "authorization": f"Bearer {bearer}"}, json={
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": PROTOCOL_VERSION, "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}},
    })
    assert r.status_code == 200, r.text
    assert r.json()["result"]["protocolVersion"] == "2025-11-25"
    return r.headers["mcp-session-id"]


def h(token: str, sid: str) -> dict[str, str]:
    return {
        "accept": ACCEPT, "authorization": f"Bearer {token}",
        "mcp-protocol-version": PROTOCOL_VERSION, "mcp-session-id": sid,
    }


async def rpc(c: httpx.AsyncClient, headers: dict[str, str], req_id: int, method: str, params=None):
    return await c.post("/mcp", headers=headers, json={"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}})


def test_discovery_documents_match_alexa_oauth_requirements():
    reset()
    async def case():
        async with await client() as c:
            prm = await c.get("/.well-known/oauth-protected-resource")
            meta = await c.get("/.well-known/oauth-authorization-server")
            assert prm.status_code == meta.status_code == 200
            assert prm.json()["resource"] == RESOURCE
            assert prm.json()["authorization_servers"] == [BASE]
            m = meta.json()
            assert "S256" in m["code_challenge_methods_supported"]
            assert {"client_credentials", "authorization_code", "refresh_token"}.issubset(m["grant_types_supported"])
    run(case())


def test_mcp_rejects_unauthenticated_without_www_authenticate():
    reset()
    async def case():
        async with await client() as c:
            r = await c.post("/mcp", headers={"accept": ACCEPT}, json={"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":PROTOCOL_VERSION}})
            assert r.status_code == 401
            assert "www-authenticate" not in {k.lower() for k in r.headers}
    run(case())


def test_service_token_initializes_and_lists_tools_but_cannot_execute_user_tools():
    reset()
    async def case():
        async with await client() as c:
            svc = await service_token(c)
            sid = await initialize(c, svc)
            ready = await c.post("/mcp", headers=h(svc, sid), json={"jsonrpc":"2.0","method":"notifications/initialized"})
            assert ready.status_code == 202
            listed = await rpc(c, h(svc, sid), 2, "tools/list")
            assert listed.status_code == 200
            names = {x["name"] for x in listed.json()["result"]["tools"]}
            assert names == {"record_change","preview_repair_plan","approve_repair_plan","execute_repair_plan","get_repair_status"}
            denied = await rpc(c, h(svc, sid), 3, "tools/call", {"name":"record_change","arguments":{"utterance":"Our flight home was cancelled. We'll land tomorrow at 18:00."}})
            assert denied.status_code == 401
    run(case())


def test_authorization_code_requires_pkce_s256_and_bad_verifier_fails():
    reset()
    async def case():
        async with await client() as c:
            missing = await c.get("/oauth/authorize", params={
                "response_type":"code","client_id":"user-client","redirect_uri":"https://client.example/callback",
                "resource":RESOURCE,"scope":"mcp:tools",
            })
            assert missing.status_code == 400
            verifier = "valid-verifier-abcdefghijklmnopqrstuvwxyz-0123456789"
            challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
            params = {"response_type":"code","client_id":"user-client","redirect_uri":"https://client.example/callback","resource":RESOURCE,"scope":"mcp:tools","code_challenge":challenge,"code_challenge_method":"S256"}
            approved = await c.post("/oauth/authorize", params=params, data={"decision":"approve", "password":"ripple-demo-password-test"})
            code = parse_qs(urlparse(approved.headers["location"]).query)["code"][0]
            bad = await c.post("/oauth/token", data={"grant_type":"authorization_code","code":code,"client_id":"user-client","redirect_uri":"https://client.example/callback","code_verifier":"wrong","resource":RESOURCE})
            assert bad.status_code == 400
            assert bad.json()["error"] == "invalid_grant"
    run(case())


def test_client_credentials_are_service_scope_only_and_no_refresh_token():
    reset()
    async def case():
        async with await client() as c:
            basic = base64.b64encode(b"svc:secret").decode()
            bad = await c.post("/oauth/token", headers={"authorization":f"Basic {basic}"}, data={"grant_type":"client_credentials","scope":"mcp:tools","resource":RESOURCE})
            assert bad.status_code == 400
            ok = await c.post("/oauth/token", headers={"authorization":f"Basic {basic}"}, data={"grant_type":"client_credentials","scope":"mcp:service","resource":RESOURCE})
            body = ok.json()
            assert body["scope"] == "mcp:service"
            assert body["expires_in"] <= 3600
            assert "refresh_token" not in body
    run(case())


def test_user_token_full_mcp_flow_is_two_phase_and_replay_safe():
    reset()
    async def case():
        async with await client() as c:
            svc = await service_token(c)
            user, _ = await user_token(c)
            sid = await initialize(c, svc)
            assert (await c.post("/mcp", headers=h(svc,sid), json={"jsonrpc":"2.0","method":"notifications/initialized"})).status_code == 202
            headers = h(user, sid)
            rec = await rpc(c, headers, 3, "tools/call", {"name":"record_change","arguments":{"utterance":"Our flight home was cancelled. We'll land tomorrow at 18:00."}})
            assert rec.status_code == 200
            preview = await rpc(c, headers, 4, "tools/call", {"name":"preview_repair_plan","arguments":{}})
            p = preview.json()["result"]["structuredContent"]
            assert p["writes_before_approval"] == 0
            card = p["repair_card"]
            assert card["display_hint"] == "inline"
            assert [m["value"] for m in card["metrics"]] == ["$116", "$42", "$74"]
            assert card["decision"]["label"] == "Approve $42 repair"
            approval = dict(p["approval_snapshot"], user_confirmed=True)
            approved = await rpc(c, headers, 5, "tools/call", {"name":"approve_repair_plan","arguments":approval})
            approved_body = approved.json()["result"]["structuredContent"]
            assert approved_body["writes"] == 0
            assert approved_body["approval_persisted"] is True
            executed = await rpc(c, headers, 6, "tools/call", {"name":"execute_repair_plan","arguments":{}})
            e = executed.json()["result"]["structuredContent"]
            assert e["receipt_count"] == 5 and e["unique_external_writes"] == 5
            replay = await rpc(c, headers, 7, "tools/call", {"name":"execute_repair_plan","arguments":{}})
            r = replay.json()["result"]["structuredContent"]
            assert r["deduplicated"] == 5 and r["unique_external_writes"] == 5
    run(case())


def test_refresh_token_issues_new_user_access_token():
    reset()
    async def case():
        async with await client() as c:
            _, refresh = await user_token(c)
            r = await c.post("/oauth/token", data={"grant_type":"refresh_token","refresh_token":refresh,"client_id":"user-client","resource":RESOURCE})
            assert r.status_code == 200
            assert r.json()["scope"] == "mcp:tools"
    run(case())


def test_origin_validation_rejects_lookalike_domain():
    reset()
    async def case():
        async with await client() as c:
            svc = await service_token(c)
            r = await c.post("/mcp", headers={"accept":ACCEPT,"authorization":f"Bearer {svc}","origin":"https://judge.example.evil.test"}, json={"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":PROTOCOL_VERSION}})
            assert r.status_code == 403
    run(case())


def test_configured_public_origin_is_allowed():
    reset()
    async def case():
        async with await client() as c:
            svc = await service_token(c)
            r = await c.post("/mcp", headers={"accept":ACCEPT,"authorization":f"Bearer {svc}","origin":"https://judge.example"}, json={"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":PROTOCOL_VERSION}})
            assert r.status_code == 200
    run(case())


def test_get_requires_auth_then_returns_405_when_sse_not_supported():
    reset()
    async def case():
        async with await client() as c:
            unauth = await c.get("/mcp")
            assert unauth.status_code == 401
            svc = await service_token(c)
            auth = await c.get("/mcp", headers={"authorization":f"Bearer {svc}"})
            assert auth.status_code == 405
    run(case())


def test_session_delete_terminates_session():
    reset()
    async def case():
        async with await client() as c:
            svc = await service_token(c)
            sid = await initialize(c, svc)
            deleted = await c.delete("/mcp", headers={"authorization":f"Bearer {svc}","mcp-session-id":sid})
            assert deleted.status_code == 204
            reuse = await rpc(c, h(svc,sid), 2, "ping")
            assert reuse.status_code == 404
    run(case())


def test_health_endpoint_is_public_and_reports_protocol():
    reset()
    async def case():
        async with await client() as c:
            r = await c.get("/healthz")
            assert r.status_code == 200
            assert r.json()["protocol"] == "2025-11-25"
            assert r.json()["version"] == "1.4.0"
    run(case())
