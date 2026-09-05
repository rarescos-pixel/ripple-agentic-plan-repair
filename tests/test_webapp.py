import pytest
from ripple.webapp import DemoController, INDEX_HTML


def test_web_demo_is_two_phase_and_replay_safe():
    c = DemoController()
    proposal = c.propose("Our flight home was cancelled. We'll land tomorrow at 18:00.")
    assert proposal["phase"] == "proposal"
    assert proposal["plan"]["impact_count"] == 5
    assert proposal["plan"]["total_added_cost"] == 42
    assert proposal["plan"]["total_avoidable_loss"] == 116
    assert proposal["plan"]["net_direct_cash_preserved"] == 74
    assert proposal["writes_before_approval"] == 0
    executed = c.approve(proposal["approval_disclosure"])
    assert executed["plan_status"] == "executed"
    assert executed["receipt_count"] == 5
    assert executed["external_write_count"] == 5
    assert all(r["status"] == "executed" for r in executed["receipts"])
    replay = c.replay()
    assert replay["deduplicated"] == 5
    assert replay["external_write_count"] == 5


def test_web_demo_primary_surface_uses_canonical_alexa_repair_card():
    c = DemoController()
    proposal = c.propose("Our flight home was cancelled. We'll land tomorrow at 18:00.")
    card = proposal["repair_card"]
    assert card["schema"] == "ripple.repair-card.v1"
    assert card["headline"] == "5 commitments affected"
    assert card["money_summary"] == "$116 at risk → $42 repair → $74 net preserved"
    assert [m["value"] for m in card["metrics"]] == ["$116", "$42", "$74"]
    assert [i["label"] for i in card["top_impacts"]] == [
        "Dinner reservation",
        "Pet care",
        "Airport pickup",
    ]
    assert card["remaining_impacts"] == 2
    assert card["decision"]["label"] == "Approve $42 repair"
    assert card["voice_summary"].endswith("Approve the $42 repair?")


def test_web_demo_html_renders_repair_card_as_primary_and_technical_evidence_secondary():
    assert "j.repair_card" in INDEX_HTML
    assert "c.money_summary" in INDEX_HTML
    assert "c.top_impacts" in INDEX_HTML
    assert "c.decision.label" in INDEX_HTML
    assert "<details><summary>Technical evidence</summary>" in INDEX_HTML
    assert "Approve this exact plan" not in INDEX_HTML
    assert "Repair the cascade, not just the calendar" not in INDEX_HTML


def test_web_demo_is_explicit_customer_to_alexa_story_without_overclaiming_transport():
    assert "rules-permitted simulated Alexa+ experience" in INDEX_HTML
    assert "Repair the cascade without opening five apps/sites." in INDEX_HTML
    assert "Customer → agent" in INDEX_HTML
    assert "Send to Alexa+" in INDEX_HTML
    assert '<div class="who">You</div>' in INDEX_HTML
    assert '<div class="who">Alexa+</div>' in INDEX_HTML
    assert "same Ripple planner, policy and receipt engine exposed by the public MCP service" in INDEX_HTML
    assert "public MCP transport is verified separately" in INDEX_HTML
    assert "does not pretend to be an official Alexa+ client" in INDEX_HTML


def test_web_demo_rejects_approve_without_proposal():
    c = DemoController()
    with pytest.raises(ValueError, match="No active proposal"):
        c.approve({})


def test_web_demo_reset_clears_execution_state():
    c = DemoController()
    p = c.propose("Our flight home was cancelled. We'll land tomorrow at 18:00.")
    c.approve(p["approval_disclosure"])
    assert len(c.tools.execution_log) == 5
    c.reset()
    assert len(c.tools.execution_log) == 0
    assert c.proposal is None


def test_web_demo_exposes_judge_relevant_dependency_and_approval_evidence():
    c = DemoController()
    proposal = c.propose("Our flight home was cancelled. We'll land tomorrow at 18:00.")
    assert len(proposal["plan"]["impacts"]) == 5
    assert all(i["dependency_path"][0] == "flight:return" for i in proposal["plan"]["impacts"])
    disclosure = proposal["approval_disclosure"]
    assert disclosure["max_total_cost"] == 42
    assert disclosure["external_people_notified"] == 3
    assert len(disclosure["external_services"]) == 5
    assert disclosure["irreversible_actions"] == ["action:1"]
    assert disclosure["snapshot_hash"] == proposal["plan"]["snapshot_hash"]


def test_web_demo_exposes_executable_adversarial_evidence():
    c = DemoController()
    evidence = c.evidence()
    assert evidence["passed"] == evidence["total"] == 7


def test_web_approval_rejects_server_side_drift_after_user_saw_snapshot():
    c = DemoController()
    p = c.propose("Our flight home was cancelled. We'll land tomorrow at 18:00.")
    visible = dict(p["approval_disclosure"])
    c.proposal.plan.actions[0].params["unexpected"] = "drift"
    with pytest.raises(ValueError, match="drift"):
        c.approve(visible)
    assert len(c.tools.execution_log) == 0


def test_web_user_time_changes_normalized_change_and_plan_snapshot():
    c = DemoController()
    a = c.propose("Our flight home was cancelled. We'll land tomorrow at 18:00.")
    av = c.proposal.change.new_value
    ah = a["plan"]["snapshot_hash"]
    b = c.propose("Our flight home was cancelled. We'll land tomorrow at 23:55.")
    bv = c.proposal.change.new_value
    bh = b["plan"]["snapshot_hash"]
    assert av.endswith("18:00:00") and bv.endswith("23:55:00")
    assert av != bv
    assert ah != bh
