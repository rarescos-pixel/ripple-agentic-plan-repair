"""Authenticated real-HTTP smoke test for Ripple MCP 2025-11-25."""
from __future__ import annotations

import base64
import hashlib
import os
from urllib.parse import parse_qs, urlparse

import httpx

BASE_URL = os.getenv("RIPPLE_SMOKE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
MCP = f"{BASE_URL}/mcp"
ACCEPT = "application/json, text/event-stream"
PROTOCOL = "2025-11-25"
SERVICE_ID = os.getenv("RIPPLE_SERVICE_CLIENT_ID", "ripple-service-test")
SERVICE_SECRET = os.getenv("RIPPLE_SERVICE_CLIENT_SECRET", "ripple-service-secret-test")
USER_ID = os.getenv("RIPPLE_USER_CLIENT_ID", "ripple-user-test")
REDIRECT = os.getenv("RIPPLE_USER_REDIRECT_URI", "http://127.0.0.1:9999/callback")
DEMO_PASSWORD = os.getenv("RIPPLE_DEMO_USER_PASSWORD", "ripple-demo-password-test")


def service_token(client: httpx.Client) -> str:
    basic = base64.b64encode(f"{SERVICE_ID}:{SERVICE_SECRET}".encode()).decode()
    response = client.post(
        f"{BASE_URL}/oauth/token",
        headers={"authorization": f"Basic {basic}"},
        data={
            "grant_type": "client_credentials",
            "scope": "mcp:service",
            "resource": MCP,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]


def user_tokens(client: httpx.Client) -> tuple[str, str]:
    verifier = "ripple-smoke-pkce-verifier-abcdefghijklmnopqrstuvwxyz-0123456789"
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    params = {
        "response_type": "code",
        "client_id": USER_ID,
        "redirect_uri": REDIRECT,
        "scope": "mcp:tools",
        "resource": MCP,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": "smoke",
    }
    authorize = client.post(
        f"{BASE_URL}/oauth/authorize",
        params=params,
        data={"decision": "approve", "password": DEMO_PASSWORD},
        follow_redirects=False,
    )
    assert authorize.status_code == 303, authorize.text
    code = parse_qs(urlparse(authorize.headers["location"]).query)["code"][0]
    token = client.post(
        f"{BASE_URL}/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": USER_ID,
            "redirect_uri": REDIRECT,
            "code_verifier": verifier,
            "resource": MCP,
        },
    )
    token.raise_for_status()
    payload = token.json()
    return payload["access_token"], payload["refresh_token"]


def verify_alexa_refresh_semantics(client: httpx.Client, refresh_token: str) -> str:
    # Alexa intentionally omits RFC 8707 `resource` during refresh.
    refreshed = client.post(
        f"{BASE_URL}/oauth/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": USER_ID,
        },
    )
    refreshed.raise_for_status()
    payload = refreshed.json()
    assert payload["token_type"] == "Bearer"
    assert payload["access_token"]
    assert "mcp:tools" in payload["scope"].split()

    # An explicitly supplied wrong resource must still fail closed.
    wrong_target = client.post(
        f"{BASE_URL}/oauth/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": USER_ID,
            "resource": "https://invalid.example/mcp",
        },
    )
    assert wrong_target.status_code == 400, wrong_target.text
    assert wrong_target.json()["error"] == "invalid_target"
    return payload["access_token"]


def call(client, headers, req_id, name, arguments=None):
    response = client.post(
        MCP,
        headers=headers,
        json={
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        },
    )
    response.raise_for_status()
    result = response.json()["result"]
    if result.get("isError"):
        raise RuntimeError(result["structuredContent"]["error"])
    return result["structuredContent"]


def main():
    with httpx.Client(timeout=15.0, follow_redirects=False) as client:
        health = client.get(f"{BASE_URL}/healthz")
        health.raise_for_status()
        readyz = client.get(f"{BASE_URL}/readyz")
        readyz.raise_for_status()
        prm = client.get(f"{BASE_URL}/.well-known/oauth-protected-resource")
        prm.raise_for_status()
        assert prm.json()["resource"] == MCP
        asm = client.get(f"{BASE_URL}/.well-known/oauth-authorization-server")
        asm.raise_for_status()

        svc = service_token(client)
        usr, refresh = user_tokens(client)
        refreshed_usr = verify_alexa_refresh_semantics(client, refresh)

        init = client.post(
            MCP,
            headers={"accept": ACCEPT, "authorization": f"Bearer {svc}"},
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": PROTOCOL,
                    "capabilities": {},
                    "clientInfo": {"name": "ripple-smoke", "version": "1.5"},
                },
            },
        )
        init.raise_for_status()
        assert init.json()["result"]["protocolVersion"] == PROTOCOL
        sid = init.headers["mcp-session-id"]
        sh = {
            "accept": ACCEPT,
            "authorization": f"Bearer {svc}",
            "mcp-protocol-version": PROTOCOL,
            "mcp-session-id": sid,
        }
        uh = {
            "accept": ACCEPT,
            "authorization": f"Bearer {refreshed_usr}",
            "mcp-protocol-version": PROTOCOL,
            "mcp-session-id": sid,
        }
        ready = client.post(
            MCP,
            headers=sh,
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        )
        assert ready.status_code == 202
        listed = client.post(
            MCP,
            headers=sh,
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        )
        listed.raise_for_status()
        tool_names = [tool["name"] for tool in listed.json()["result"]["tools"]]

        change = call(
            client,
            uh,
            3,
            "record_change",
            {"utterance": "Our flight home was cancelled. We'll land tomorrow at 18:00."},
        )
        preview = call(client, uh, 4, "preview_repair_plan")
        assert preview["writes_before_approval"] == 0
        approval = dict(preview["approval_snapshot"], user_confirmed=True)
        approved = call(client, uh, 5, "approve_repair_plan", approval)
        assert approved["writes"] == 0
        executed = call(client, uh, 6, "execute_repair_plan")
        assert executed["receipt_count"] == 5 and executed["unique_external_writes"] == 5
        replay = call(client, uh, 7, "execute_repair_plan")
        assert replay["deduplicated"] == 5 and replay["unique_external_writes"] == 5
        deleted = client.delete(
            MCP,
            headers={"authorization": f"Bearer {svc}", "mcp-session-id": sid},
        )
        assert deleted.status_code == 204

        print("Ripple authenticated MCP smoke: PASS")
        print("base:", BASE_URL)
        print("protocol:", PROTOCOL)
        print("oauth_refresh_without_resource: PASS")
        print("oauth_refresh_wrong_resource: rejected")
        print("tools:", ", ".join(tool_names))
        print("change:", change["change"]["new_value"])
        print("preview:", preview["plan"]["impact_count"], "impacts /", preview["writes_before_approval"], "writes")
        print("approval writes:", approved["writes"])
        print("execute:", executed["receipt_count"], "receipts /", executed["unique_external_writes"], "unique writes")
        print("replay:", replay["deduplicated"], "deduplicated /", replay["unique_external_writes"], "unique writes")


if __name__ == "__main__":
    main()
