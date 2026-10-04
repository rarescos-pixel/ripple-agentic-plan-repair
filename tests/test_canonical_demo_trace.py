import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_canonical_demo_trace_is_deterministic_product_truth(tmp_path):
    output = tmp_path / "trace.json"
    subprocess.run(
        [sys.executable, "scripts/canonical_demo_trace.py", "--output", str(output)],
        cwd=ROOT,
        check=True,
        env={**__import__("os").environ, "PYTHONPATH": "src"},
    )
    trace = json.loads(output.read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "docs/CANONICAL_DEMO_TRACE.schema.json").read_text(encoding="utf-8"))

    assert trace["schema_version"] == schema["properties"]["schema_version"]["const"] == "1.0.0"
    assert trace["render"] == {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "nominal_duration_frames": 4050,
    }
    assert trace["scenario"]["provider_class"] == "deterministic-digital-twin"
    assert trace["scenario"]["host_class"] == "simulated-alexa-plus-host"

    beats = trace["beats"]
    frames = [b["frame"] for b in beats]
    assert frames == sorted(frames)
    assert len(frames) == len(set(frames))
    assert all(0 <= frame < 4050 for frame in frames)

    by_id = {b["id"]: b for b in beats}
    required = {
        "draft",
        "meaning_confirmed",
        "initial_plan",
        "initial_action_approved",
        "mom_leaves",
        "repair_after_mom_leaves",
        "repair_after_mom_leaves_approved",
        "due_repair_executed",
        "departure_delayed",
        "exact_approval",
        "old_departure_no_effect",
        "wait_for_departure_evidence",
        "family_departed_evidence",
        "final_exact_approval",
        "verified_execution",
        "session_reconstructed",
        "replay_deduplicated",
        "completion_verified",
    }
    assert set(by_id) == required

    # The confirmed meaning never silently changes while the world and plan do.
    assert {b["state"]["contract_version"] for b in beats} == {1}
    assert by_id["meaning_confirmed"]["state"]["write_count"] == 0
    assert by_id["initial_action_approved"]["state"]["write_count"] == 0

    # Hero invariant: Mom leaving changes an assumption, never her access authority.
    mom = by_id["mom_leaves"]["state"]
    assert mom["assumptions"]["guest_stays"] is False
    assert mom["world_facts"]["guest_access"] is True
    assert mom["decision"] == "REQUEST_APPROVAL"
    for beat in beats:
        facts = beat["state"]["world_facts"]
        if facts is not None and "guest_access" in facts:
            assert facts["guest_access"] is True
        for action in beat["state"]["plan"]["actions"]:
            assert "guest_access" not in action.get("writes", {})

    delayed = by_id["departure_delayed"]["state"]
    assert "departure_timing" in delayed["threat"]["violations"]

    # Scheduled time is not evidence. This beat must be effect-free.
    old = by_id["old_departure_no_effect"]["state"]
    held = by_id["wait_for_departure_evidence"]["state"]
    assert held["decision"] == "WAIT_FOR_EVIDENCE"
    assert held["write_count"] == old["write_count"]

    executed = by_id["verified_execution"]["state"]
    rebuilt = by_id["session_reconstructed"]["state"]
    replay = by_id["replay_deduplicated"]["state"]
    assert executed["verified_receipts"] >= 1
    assert rebuilt["session_generation"] == 2
    assert rebuilt["contract_id"] == executed["contract_id"]
    assert rebuilt["verified_receipts"] == executed["verified_receipts"]
    assert replay["write_count"] == rebuilt["write_count"]
    assert replay["verified_receipts"] == rebuilt["verified_receipts"]

    completed = by_id["completion_verified"]["state"]
    assert completed["phase"] == "SATISFIED"
    assert completed["contract_version"] == 1
