from starlette.testclient import TestClient

from ripple.asgi import app


GOLDEN_UTTERANCE = "Our flight home was cancelled. We'll land tomorrow at 18:00."


def _client() -> TestClient:
    return TestClient(app, base_url="https://testserver")


def test_public_judge_demo_mount_rewrites_api_paths_and_sets_safe_headers():
    with _client() as client:
        response = client.get("/demo")
        assert response.status_code == 200
        assert "rules-permitted simulated Alexa+ experience" in response.text
        assert "Repair the cascade without opening five apps/sites." in response.text
        assert "post('/demo/api/propose'" in response.text
        assert "get('/demo/api/evidence'" in response.text
        assert response.headers["cache-control"] == "no-store"
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
        assert "ripple_demo_sid=" in response.headers["set-cookie"]
        assert "HttpOnly" in response.headers["set-cookie"]
        assert "Secure" in response.headers["set-cookie"]


def test_public_judge_demo_runs_two_phase_golden_flow_and_replay_safely():
    with _client() as client:
        client.get("/demo")
        proposal_response = client.post("/demo/api/propose", json={"utterance": GOLDEN_UTTERANCE})
        assert proposal_response.status_code == 200
        proposal = proposal_response.json()
        assert proposal["phase"] == "proposal"
        assert proposal["plan"]["impact_count"] == 5
        assert proposal["plan"]["total_avoidable_loss"] == 116
        assert proposal["plan"]["total_added_cost"] == 42
        assert proposal["plan"]["net_direct_cash_preserved"] == 74
        assert proposal["writes_before_approval"] == 0

        approval_response = client.post("/demo/api/approve", json=proposal["approval_disclosure"])
        assert approval_response.status_code == 200
        executed = approval_response.json()
        assert executed["plan_status"] == "executed"
        assert executed["receipt_count"] == 5
        assert executed["external_write_count"] == 5

        replay_response = client.post("/demo/api/replay", json={})
        assert replay_response.status_code == 200
        replay = replay_response.json()
        assert replay["receipt_count"] == 5
        assert replay["deduplicated"] == 5
        assert replay["external_write_count"] == 5


def test_public_judge_demo_browser_sessions_do_not_share_approval_state():
    with _client() as first, _client() as second:
        first.get("/demo")
        second.get("/demo")
        proposal = first.post("/demo/api/propose", json={"utterance": GOLDEN_UTTERANCE}).json()
        first_approval = first.post("/demo/api/approve", json=proposal["approval_disclosure"])
        assert first_approval.status_code == 200

        second_replay = second.post("/demo/api/replay", json={})
        assert second_replay.status_code == 400
        assert "No active proposal" in second_replay.json()["error"]


def test_public_judge_demo_rejects_empty_change():
    with _client() as client:
        client.get("/demo")
        response = client.post("/demo/api/propose", json={"utterance": "   "})
        assert response.status_code == 400
        assert response.json()["error"] == "utterance is required"
