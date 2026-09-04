"""Authenticated end-to-end latency probe for the Alexa+ MCP customer path.

The Alexa+ MCP QuickStart requires round-trip query response latency below
500 ms. This probe measures real HTTP requests against the deployed server,
after authentication and session setup, so token acquisition does not pollute
the per-query measurements.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import time
from urllib.parse import parse_qs, urlparse

import httpx

from ripple.evaluation.latency import LatencyStats, latency_gate, summarize_latencies

BASE_URL = os.getenv("RIPPLE_SMOKE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
MCP = f"{BASE_URL}/mcp"
ACCEPT = "application/json, text/event-stream"
PROTOCOL = "2025-11-25"
SERVICE_ID = os.getenv("RIPPLE_SERVICE_CLIENT_ID", "ripple-service-test")
SERVICE_SECRET = os.getenv("RIPPLE_SERVICE_CLIENT_SECRET", "ripple-service-secret-test")
USER_ID = os.getenv("RIPPLE_USER_CLIENT_ID", "ripple-user-test")
REDIRECT = os.getenv("RIPPLE_USER_REDIRECT_URI", "http://127.0.0.1:9999/callback")
DEMO_PASSWORD = os.getenv("RIPPLE_DEMO_USER_PASSWORD", "ripple-demo-password-test")
COUNT = int(os.getenv("RIPPLE_LATENCY_SAMPLES", "20"))
WARMUP = int(os.getenv("RIPPLE_LATENCY_WARMUP", "2"))
LIMIT_MS = float(os.getenv("RIPPLE_LATENCY_LIMIT_MS", "500"))
UTTERANCE = os.getenv(
    "RIPPLE_LATENCY_UTTERANCE",
    "Our flight home was cancelled. We'll land tomorrow at 18:00.",
)


def _service_token(client: httpx.Client) -> str:
    basic = base64.b64encode(f"{SERVICE_ID}:{SERVICE_SECRET}".encode()).decode()
    response = client.post(
        f"{BASE_URL}/oauth/token",
        headers={"authorization": f"Basic {basic}"},
        data={"grant_type": "client_credentials", "scope": "mcp:service", "resource": MCP},
    )
    response.raise_for_status()
    return str(response.json()["access_token"])


def _user_token(client: httpx.Client) -> str:
    verifier = "ripple-latency-pkce-verifier-abcdefghijklmnopqrstuvwxyz-0123456789"
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    params = {
        "response_type": "code",
        "client_id": USER_ID,
        "redirect_uri": REDIRECT,
        "scope": "mcp:tools",
        "resource": MCP,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": "latency",
    }
    authorization = client.post(
        f"{BASE_URL}/oauth/authorize",
        params=params,
        data={"decision": "approve", "password": DEMO_PASSWORD},
        follow_redirects=False,
    )
    if authorization.status_code != 303:
        raise RuntimeError(f"authorization failed: {authorization.status_code} {authorization.text}")
    code = parse_qs(urlparse(authorization.headers["location"]).query)["code"][0]
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
    return str(token.json()["access_token"])


def _rpc(client: httpx.Client, headers: dict[str, str], req_id: int, method: str, params=None) -> httpx.Response:
    response = client.post(
        MCP,
        headers=headers,
        json={"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}},
    )
    response.raise_for_status()
    body = response.json()
    if "error" in body:
        raise RuntimeError(f"MCP error for {method}: {body['error']}")
    return response


def _tool_call(client: httpx.Client, headers: dict[str, str], req_id: int, name: str, arguments=None) -> dict:
    response = _rpc(
        client,
        headers,
        req_id,
        "tools/call",
        {"name": name, "arguments": arguments or {}},
    )
    result = response.json()["result"]
    if result.get("isError"):
        raise RuntimeError(f"tool {name} failed: {result['structuredContent'].get('error')}")
    return dict(result["structuredContent"])


def _measure(fn, *, samples: int, warmup: int) -> list[float]:
    for _ in range(max(0, warmup)):
        fn()
    values: list[float] = []
    for _ in range(samples):
        started = time.perf_counter()
        fn()
        values.append((time.perf_counter() - started) * 1000.0)
    return values


def main() -> None:
    if COUNT <= 0:
        raise SystemExit("RIPPLE_LATENCY_SAMPLES must be positive")
    if LIMIT_MS <= 0:
        raise SystemExit("RIPPLE_LATENCY_LIMIT_MS must be positive")

    timeout = max(5.0, LIMIT_MS / 1000.0 * 4.0)
    with httpx.Client(timeout=timeout, follow_redirects=False) as client:
        service = _service_token(client)
        user = _user_token(client)
        initialized = client.post(
            MCP,
            headers={"accept": ACCEPT, "authorization": f"Bearer {service}"},
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": PROTOCOL,
                    "capabilities": {},
                    "clientInfo": {"name": "ripple-latency-probe", "version": "1.5"},
                },
            },
        )
        initialized.raise_for_status()
        sid = initialized.headers["mcp-session-id"]
        service_headers = {
            "accept": ACCEPT,
            "authorization": f"Bearer {service}",
            "mcp-protocol-version": PROTOCOL,
            "mcp-session-id": sid,
        }
        user_headers = {
            "accept": ACCEPT,
            "authorization": f"Bearer {user}",
            "mcp-protocol-version": PROTOCOL,
            "mcp-session-id": sid,
        }
        ready = client.post(
            MCP,
            headers=service_headers,
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        )
        if ready.status_code != 202:
            raise RuntimeError(f"session initialization notification failed: {ready.status_code}")

        req = 10

        def next_id() -> int:
            nonlocal req
            req += 1
            return req

        # Seed proposal state before measuring preview/status. No writes occur.
        _tool_call(client, user_headers, next_id(), "record_change", {"utterance": UTTERANCE})

        probes = {
            "ping": lambda: _rpc(client, service_headers, next_id(), "ping"),
            "tools/list": lambda: _rpc(client, service_headers, next_id(), "tools/list"),
            "record_change": lambda: _tool_call(
                client, user_headers, next_id(), "record_change", {"utterance": UTTERANCE}
            ),
            "preview_repair_plan": lambda: _tool_call(
                client, user_headers, next_id(), "preview_repair_plan"
            ),
            "get_repair_status": lambda: _tool_call(
                client, user_headers, next_id(), "get_repair_status"
            ),
        }

        stats: list[LatencyStats] = []
        try:
            for operation, probe in probes.items():
                samples = _measure(probe, samples=COUNT, warmup=WARMUP)
                stats.append(summarize_latencies(operation, samples, limit_ms=LIMIT_MS))
        finally:
            client.delete(
                MCP,
                headers={"authorization": f"Bearer {service}", "mcp-session-id": sid},
            )

    result = {
        "status": "PASS" if latency_gate(stats) else "FAIL",
        "base_url": BASE_URL,
        "protocol": PROTOCOL,
        "limit_ms": LIMIT_MS,
        "samples_per_operation": COUNT,
        "warmup_per_operation": WARMUP,
        "operations": [row.as_dict() for row in stats],
    }
    print("RIPPLE_MCP_LATENCY_BEGIN")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("RIPPLE_MCP_LATENCY_END")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
