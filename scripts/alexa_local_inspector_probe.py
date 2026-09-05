"""Probe the documented Alexa+ Local Inspector MCP request shape over real HTTP."""
from __future__ import annotations

import base64
import os

import httpx

BASE_URL = os.getenv("RIPPLE_SMOKE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
MCP = f"{BASE_URL}/mcp"
PROTOCOL = "2025-11-25"
SERVICE_ID = os.getenv("RIPPLE_SERVICE_CLIENT_ID", "ripple-service-test")
SERVICE_SECRET = os.getenv("RIPPLE_SERVICE_CLIENT_SECRET", "ripple-service-secret-test")


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


def main() -> None:
    with httpx.Client(timeout=15.0, follow_redirects=False) as client:
        token = service_token(client)

        unauth = client.post(
            MCP,
            headers={"accept": "application/json"},
            json={
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {"protocolVersion": "2025-06-18"},
            },
        )
        assert unauth.status_code == 401, unauth.text
        assert "www-authenticate" not in {key.lower() for key in unauth.headers}

        init = client.post(
            MCP,
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
        init.raise_for_status()
        assert init.json()["result"]["protocolVersion"] == PROTOCOL
        sid = init.headers["mcp-session-id"]

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {token}",
            "mcp-protocol-version": PROTOCOL,
            "mcp-session-id": sid,
        }
        initialized = client.post(
            MCP,
            headers=headers,
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        )
        assert initialized.status_code == 202, initialized.text

        tools = client.post(
            MCP,
            headers=headers,
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        )
        tools.raise_for_status()
        listed_tools = tools.json()["result"]["tools"]
        assert len(listed_tools) == 5
        preview = next(t for t in listed_tools if t["name"] == "preview_repair_plan")
        resource_uri = preview["_meta"]["ui"]["resourceUri"]
        assert resource_uri.startswith("ui://ripple/")

        resource = client.post(
            MCP,
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "resources/read",
                "params": {"uri": resource_uri},
            },
        )
        resource.raise_for_status()
        contents = resource.json()["result"]["contents"]
        assert contents[0]["mimeType"] == "text/html;profile=mcp-app"

        deleted = client.delete(
            MCP,
            headers={"authorization": f"Bearer {token}", "mcp-session-id": sid},
        )
        assert deleted.status_code == 204

        print("Ripple Alexa Local Inspector request-shape probe: PASS")
        print("base:", BASE_URL)
        print("accept: application/json")
        print("client_protocol_example: 2025-06-18")
        print("server_protocol:", PROTOCOL)
        print("unauth_401_without_www_authenticate: PASS")
        print("tools: 5")
        print("repair_card_resource:", resource_uri)
        print("repair_card_mime: text/html;profile=mcp-app")


if __name__ == "__main__":
    main()
