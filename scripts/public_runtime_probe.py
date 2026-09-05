"""Read-only proof that the deployed public Ripple endpoint matches the expected release.

This probe intentionally uses no production secrets. It verifies public health/readiness,
source revision pinning, and the unauthenticated Alexa Local Inspector request shape.
"""
from __future__ import annotations

import os

import httpx

BASE_URL = os.getenv(
    "RIPPLE_SMOKE_BASE_URL",
    "https://ripple-v12-production.up.railway.app",
).rstrip("/")
EXPECTED_SOURCE_SHA = os.getenv("RIPPLE_EXPECTED_SOURCE_SHA", "").strip().lower()
PROTOCOL = "2025-11-25"


def main() -> None:
    with httpx.Client(timeout=20.0, follow_redirects=False) as client:
        health = client.get(f"{BASE_URL}/healthz")
        health.raise_for_status()
        health_payload = health.json()
        assert health_payload["status"] == "ok", health_payload
        assert health_payload["protocol"] == PROTOCOL, health_payload

        ready = client.get(f"{BASE_URL}/readyz")
        ready.raise_for_status()
        readiness = ready.json()
        assert readiness["status"] == "ready", readiness
        source_revision = readiness.get("source_revision")
        if EXPECTED_SOURCE_SHA:
            assert source_revision == EXPECTED_SOURCE_SHA, (
                f"Public source drift: expected {EXPECTED_SOURCE_SHA}, got {source_revision}"
            )

        # Reproduce the documented Alexa Local Inspector JSON-only request shape
        # without credentials. The important public transport proof here is that
        # JSON-only Accept reaches authentication and is not rejected with 406.
        unauth = client.post(
            f"{BASE_URL}/mcp",
            headers={"accept": "application/json"},
            json={
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {"protocolVersion": "2025-06-18"},
            },
        )
        assert unauth.status_code == 401, (
            f"Expected JSON-only Inspector-shaped request to reach auth (401), "
            f"got {unauth.status_code}: {unauth.text}"
        )

        print("Ripple public runtime proof: PASS")
        print("base:", BASE_URL)
        print("source revision:", source_revision or "unavailable")
        print("runtime mode:", readiness.get("runtime_mode", "unavailable"))
        print("structural AWS runtime:", readiness.get("structural_aws_runtime"))
        print("AWS components:", readiness.get("aws_components"))
        print("Alexa Local Inspector JSON-only Accept reaches authentication: PASS")


if __name__ == "__main__":
    main()
