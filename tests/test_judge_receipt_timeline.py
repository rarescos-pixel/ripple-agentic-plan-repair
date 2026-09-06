from __future__ import annotations

from ripple.domain.models import Approval
from ripple.golden import build_golden
from ripple.presentation import build_receipt_timeline, build_repair_card
from ripple.presentation.mcp_app import REPAIR_CARD_APP_HTML


def _approved_golden():
    _, tools, planner, executor, change = build_golden()
    plan = planner.build_plan(change)
    approval = Approval(plan.id, plan.version, 42, 3, plan.snapshot_hash())
    return tools, executor, plan, approval


def test_repair_card_explains_deterministic_selection_without_granting_llm_authority():
    _, _, plan, _ = _approved_golden()
    card = build_repair_card(plan)
    policy = card["selection_policy"]
    assert policy["label"] == "Why this plan?"
    assert "Deterministic policy" in policy["summary"]
    assert "model does not choose spending" in policy["summary"]


def test_first_execution_timeline_is_compact_and_receipt_backed():
    tools, executor, plan, approval = _approved_golden()
    receipts = executor.execute(plan, approval)
    timeline = build_receipt_timeline(
        plan,
        receipts,
        authoritative_unique_writes=len(tools.execution_log),
    )
    assert timeline["headline"] == "Repair complete"
    assert timeline["proof_summary"] == "5 actions → 5 receipts → 5 provider writes"
    assert timeline["counts"] == {
        "actions": 5,
        "receipts": 5,
        "executed_this_call": 5,
        "deduplicated_this_call": 0,
        "failed_this_call": 0,
        "authoritative_unique_writes": 5,
        "duplicate_provider_writes": 0,
    }
    assert len(timeline["entries"]) == 5
    rendered = repr(timeline)
    assert "idempotency_key" not in rendered
    assert "snapshot_hash" not in rendered
    assert "params" not in rendered


def test_replay_timeline_makes_zero_duplicate_provider_writes_visible():
    tools, executor, plan, approval = _approved_golden()
    executor.execute(plan, approval)
    replay = executor.execute(plan, approval)
    timeline = build_receipt_timeline(
        plan,
        replay,
        authoritative_unique_writes=len(tools.execution_log),
    )
    assert timeline["headline"] == "Replay safe"
    assert timeline["proof_summary"] == "5 replayed → 5 deduplicated → 0 new provider writes"
    assert timeline["counts"]["deduplicated_this_call"] == 5
    assert timeline["counts"]["authoritative_unique_writes"] == 5
    assert timeline["counts"]["duplicate_provider_writes"] == 0
    assert timeline["safety_note"] == "Replay produced 0 duplicate provider writes."


def test_mcp_app_can_render_both_decision_and_execution_proof_without_write_ui():
    assert "Why this plan?" in REPAIR_CARD_APP_HTML
    assert "receipt_timeline" in REPAIR_CARD_APP_HTML
    assert "Safety receipt" in REPAIR_CARD_APP_HTML
    assert "Approve" not in REPAIR_CARD_APP_HTML or "role=\"note\"" in REPAIR_CARD_APP_HTML
    assert "ui/tools/call" not in REPAIR_CARD_APP_HTML
