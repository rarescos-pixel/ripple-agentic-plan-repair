from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any

import httpx

DEFAULT_BASE_URL = "https://ripple-v12-production.up.railway.app"
GOLDEN_UTTERANCE = "Our flight home was cancelled. We'll land tomorrow at 18:00."


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _wait_for_revision(
    client: httpx.Client,
    expected_revision: str | None,
    *,
    attempts: int,
    interval_seconds: float,
) -> dict[str, Any]:
    last_error = "no readiness response"
    for attempt in range(1, attempts + 1):
        try:
            response = client.get("/readyz")
            if response.status_code == 200:
                body = response.json()
                observed = str(body.get("source_revision") or "").lower()
                if expected_revision is None or observed == expected_revision.lower():
                    return body
                last_error = f"source_revision={observed or '<missing>'} expected={expected_revision.lower()}"
            else:
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
        except Exception as exc:  # network/deploy transition
            last_error = repr(exc)
        if attempt < attempts:
            print(f"WAIT deployment {attempt}/{attempts}: {last_error}", flush=True)
            time.sleep(interval_seconds)
    raise RuntimeError(f"Timed out waiting for exact production revision: {last_error}")


def run_smoke(
    base_url: str,
    *,
    expected_revision: str | None = None,
    attempts: int = 60,
    interval_seconds: float = 5.0,
    timeout_seconds: float = 20.0,
) -> None:
    base_url = base_url.rstrip("/")
    with httpx.Client(base_url=base_url, timeout=timeout_seconds, follow_redirects=True) as client:
        ready = _wait_for_revision(
            client,
            expected_revision,
            attempts=attempts,
            interval_seconds=interval_seconds,
        )
        _require(ready.get("status") == "ready", "readyz status must be ready")

        demo = client.get("/demo")
        _require(demo.status_code == 200, f"demo GET failed: {demo.status_code}")
        _require("rules-permitted simulated Alexa+ experience" in demo.text, "demo truth label missing")
        _require("Repair the cascade without opening five apps/sites." in demo.text, "demo value promise missing")
        _require("/demo/api/propose" in demo.text, "demo API mount missing")

        evidence_response = client.get("/demo/api/evidence")
        _require(evidence_response.status_code == 200, "demo evidence endpoint failed")
        evidence = evidence_response.json()
        _require(evidence.get("passed") == evidence.get("total") == 7, f"adversarial evidence mismatch: {evidence}")

        proposal_response = client.post("/demo/api/propose", json={"utterance": GOLDEN_UTTERANCE})
        _require(proposal_response.status_code == 200, f"proposal failed: {proposal_response.text[:300]}")
        proposal = proposal_response.json()
        plan = proposal.get("plan") or {}
        _require(plan.get("impact_count") == 5, f"expected 5 impacts: {plan}")
        _require(plan.get("total_avoidable_loss") == 116, f"expected $116 at risk: {plan}")
        _require(plan.get("total_added_cost") == 42, f"expected $42 repair: {plan}")
        _require(plan.get("net_direct_cash_preserved") == 74, f"expected $74 preserved: {plan}")
        _require(proposal.get("writes_before_approval") == 0, "proposal performed external writes")

        approval = proposal.get("approval_disclosure")
        _require(isinstance(approval, dict), "approval disclosure missing")
        approve_response = client.post("/demo/api/approve", json=approval)
        _require(approve_response.status_code == 200, f"approval/execute failed: {approve_response.text[:300]}")
        executed = approve_response.json()
        _require(executed.get("plan_status") == "executed", f"plan did not execute: {executed}")
        _require(executed.get("receipt_count") == 5, f"expected 5 receipts: {executed}")
        _require(executed.get("external_write_count") == 5, f"expected 5 unique writes: {executed}")

        replay_response = client.post("/demo/api/replay", json={})
        _require(replay_response.status_code == 200, f"replay failed: {replay_response.text[:300]}")
        replay = replay_response.json()
        _require(replay.get("receipt_count") == 5, f"expected 5 replay receipts: {replay}")
        _require(replay.get("deduplicated") == 5, f"expected 5/5 deduplicated replay: {replay}")
        _require(replay.get("external_write_count") == 5, f"replay created duplicate writes: {replay}")

    print("RIPPLE_PUBLIC_JUDGE_DEMO_SMOKE: PASS")
    print(f"base_url: {base_url}")
    if expected_revision:
        print(f"source_revision: {expected_revision.lower()}")
    print("conversation: 5 impacts -> $116 at risk -> $42 repair -> $74 preserved")
    print("approval: 0 pre-approval writes -> 5 receipts / 5 unique simulated writes")
    print("replay: 5/5 deduplicated -> unique simulated writes remain 5")
    print("adversarial_matrix: 7/7 PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the public Ripple judge demo on an exact deployed source revision.")
    parser.add_argument("--base-url", default=os.getenv("RIPPLE_PUBLIC_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--expected-source-revision", default=os.getenv("EXPECTED_SOURCE_REVISION") or None)
    parser.add_argument("--attempts", type=int, default=60)
    parser.add_argument("--interval-seconds", type=float, default=5.0)
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    args = parser.parse_args()
    try:
        run_smoke(
            args.base_url,
            expected_revision=args.expected_source_revision,
            attempts=args.attempts,
            interval_seconds=args.interval_seconds,
            timeout_seconds=args.timeout_seconds,
        )
    except Exception as exc:
        print(f"RIPPLE_PUBLIC_JUDGE_DEMO_SMOKE: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
