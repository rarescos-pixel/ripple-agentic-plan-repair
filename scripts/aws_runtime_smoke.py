"""Independent public-endpoint proof for Ripple's structural AWS runtime.

Run only after the Railway service has been cut over to DynamoDB + Bedrock +
CloudWatch. The script proves Bedrock normalization from the returned ChangeEvent
and DynamoDB durability by destroying the first MCP session and requiring a
fresh session to deduplicate the exact same five provider writes.
"""
from __future__ import annotations

import os

import httpx

from mcp_smoke import (
    ACCEPT,
    BASE_URL,
    MCP,
    PROTOCOL,
    call,
    service_token,
    user_token,
)


UTTERANCE = os.getenv(
    "RIPPLE_SMOKE_UTTERANCE",
    "Our flight home was cancelled. We'll land tomorrow at 18:00.",
)


def open_session(client: httpx.Client, service_access: str, user_access: str, req_id: int):
    init = client.post(
        MCP,
        headers={"accept": ACCEPT, "authorization": f"Bearer {service_access}"},
        json={
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL,
                "capabilities": {},
                "clientInfo": {"name": "ripple-aws-runtime-smoke", "version": "1.5"},
            },
        },
    )
    init.raise_for_status()
    assert init.json()["result"]["protocolVersion"] == PROTOCOL
    sid = init.headers["mcp-session-id"]
    service_headers = {
        "accept": ACCEPT,
        "authorization": f"Bearer {service_access}",
        "mcp-protocol-version": PROTOCOL,
        "mcp-session-id": sid,
    }
    user_headers = {
        "accept": ACCEPT,
        "authorization": f"Bearer {user_access}",
        "mcp-protocol-version": PROTOCOL,
        "mcp-session-id": sid,
    }
    initialized = client.post(
        MCP,
        headers=service_headers,
        json={"jsonrpc": "2.0", "method": "notifications/initialized"},
    )
    assert initialized.status_code == 202
    return sid, service_headers, user_headers


def close_session(client: httpx.Client, service_access: str, sid: str) -> None:
    response = client.delete(
        MCP,
        headers={"authorization": f"Bearer {service_access}", "mcp-session-id": sid},
    )
    assert response.status_code == 204


def execute_cycle(client: httpx.Client, service_access: str, user_access: str, req_id: int):
    sid, _, user_headers = open_session(client, service_access, user_access, req_id)
    changed = call(client, user_headers, req_id + 1, "record_change", {"utterance": UTTERANCE})
    preview = call(client, user_headers, req_id + 2, "preview_repair_plan")
    assert preview["writes_before_approval"] == 0
    approval = dict(preview["approval_snapshot"], user_confirmed=True)
    approved = call(client, user_headers, req_id + 3, "approve_repair_plan", approval)
    assert approved["writes"] == 0
    executed = call(client, user_headers, req_id + 4, "execute_repair_plan")
    assert executed["receipt_count"] == 5
    replay = call(client, user_headers, req_id + 5, "execute_repair_plan")
    assert replay["deduplicated"] == 5
    return sid, changed, preview, executed, replay


def main() -> None:
    with httpx.Client(timeout=30.0, follow_redirects=False) as client:
        health = client.get(f"{BASE_URL}/healthz")
        health.raise_for_status()
        ready = client.get(f"{BASE_URL}/readyz")
        ready.raise_for_status()

        service_access = service_token(client)
        user_access = user_token(client)

        first_sid, first_change, first_preview, first_execute, first_replay = execute_cycle(
            client, service_access, user_access, 100
        )
        change = first_change["change"]
        assert change["id"].startswith("change:bedrock:"), change
        assert change["correlation_id"].startswith("bedrock:"), change
        assert first_preview["plan"]["impact_count"] == 5
        assert first_replay["deduplicated"] == 5
        close_session(client, service_access, first_sid)

        # A fresh session creates a fresh ToolRegistry and executor. Five
        # deduplicated receipts with zero provider writes therefore require the
        # authoritative receipts to have survived outside MCP session memory.
        second_sid, second_change, second_preview, second_execute, _ = execute_cycle(
            client, service_access, user_access, 200
        )
        assert second_change["change"]["id"] == change["id"]
        assert second_change["change"]["correlation_id"].startswith("bedrock:")
        assert second_change["change"]["correlation_id"] != change["correlation_id"]
        assert second_preview["approval_snapshot"]["snapshot_hash"] == first_preview["approval_snapshot"]["snapshot_hash"]
        assert second_execute["deduplicated"] == 5
        assert second_execute["unique_external_writes"] == 0
        close_session(client, service_access, second_sid)

        print("Ripple AWS runtime smoke: PASS")
        print("Bedrock normalization: PASS")
        print("fresh-session durable replay: 5/5 deduplicated, 0 provider writes")
        print("base:", BASE_URL)
        print("change id:", change["id"])
        print("trace correlation:", change["correlation_id"])
        print("net preserved:", first_preview["plan"]["net_direct_cash_preserved"])
        print("first-cycle provider writes:", first_execute["unique_external_writes"])


if __name__ == "__main__":
    main()
