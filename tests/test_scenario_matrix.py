import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from ripple.domain.models import PlanNode, NodeKind, DependencyEdge, ChangeEvent, Approval
from ripple.tools.simulated import ToolRegistry
from ripple.engine.dependency import DependencyEngine
from ripple.orchestration.planner import Planner
from ripple.orchestration.executor import Executor, SimulatedInterruption
from ripple.golden import build_golden


def test_missed_cancellation_deadline_stays_visible_and_unresolved():
    nodes = {
        "flight:return": PlanNode("flight:return", NodeKind.FACT, "Return flight"),
        "reservation:D1": PlanNode(
            "reservation:D1", NodeKind.RESERVATION, "Dinner reservation",
            start_at="2026-09-10T20:00:00", financial_exposure=60,
            attributes={"deadline_missed": True, "deadline_minutes": -5, "urgency": 100},
        ),
    }
    edges = [DependencyEdge("flight:return", "reservation:D1", "arrival_dependency", condition="arrival_after_start")]
    change = ChangeEvent("c", "flight:return", "arrival_at", "2026-09-10T18:00:00", "2026-09-11T18:00:00")
    plan = Planner(nodes, DependencyEngine(nodes, edges, ToolRegistry())).build_plan(change)
    assert len(plan.impacts) == 1
    assert len(plan.actions) == 0
    assert plan.unresolved_items == ["reservation:D1"]
    assert plan.total_avoidable_loss == 0


def test_ambiguous_provider_state_blocks_entire_plan_before_writes():
    nodes, _, _, _, change = build_golden()
    tools = ToolRegistry(ambiguous_operations={"reschedule_delivery"})
    edges = [DependencyEdge("flight:return", nid, "arrival_dependency") for nid in nodes if nid != "flight:return"]
    plan = Planner(nodes, DependencyEngine(nodes, edges, tools)).build_plan(change)
    approval = Approval(plan.id, plan.version, 42, 3, plan.snapshot_hash())
    with pytest.raises(ValueError, match="Provider state ambiguous"):
        Executor(tools).execute(plan, approval)
    assert tools.execution_log == []


def test_explicit_hard_preference_beats_cheaper_repair():
    nodes = {
        "flight:return": PlanNode("flight:return", NodeKind.FACT, "Return flight"),
        "reservation:D1": PlanNode(
            "reservation:D1", NodeKind.RESERVATION, "Anniversary dinner",
            start_at="2026-09-10T20:00:00", financial_exposure=100,
            attributes={
                "deadline_minutes": 30,
                "new_start_at": "2026-09-11T20:00:00",
                "reschedule_cost": 25,
                "disallowed_operations": ["cancel_reservation"],
                "urgency": 90,
            },
        ),
    }
    edges = [DependencyEdge("flight:return", "reservation:D1", "arrival_dependency", condition="arrival_after_start")]
    change = ChangeEvent("c", "flight:return", "arrival_at", "2026-09-10T18:00:00", "2026-09-11T18:00:00")
    plan = Planner(nodes, DependencyEngine(nodes, edges, ToolRegistry())).build_plan(change)
    assert len(plan.actions) == 1
    assert plan.actions[0].operation == "reschedule_reservation"
    assert plan.actions[0].added_cost == 25


def test_content_drift_after_approval_requires_reapproval_even_without_version_bump():
    _, tools, planner, executor, change = build_golden()
    plan = planner.build_plan(change)
    approval = Approval(plan.id, plan.version, 42, 3, plan.snapshot_hash())
    plan.actions[0].params["new_start_at"] = "2026-09-11T19:30:00"
    with pytest.raises(ValueError, match="content drifted"):
        executor.execute(plan, approval)
    assert tools.execution_log == []


def test_interrupted_execution_recovers_without_duplicate_writes():
    _, tools, planner, executor, change = build_golden()
    plan = planner.build_plan(change)
    approval = Approval(plan.id, plan.version, 42, 3, plan.snapshot_hash())
    with pytest.raises(SimulatedInterruption):
        executor.execute(plan, approval, interrupt_after=2)
    assert len(tools.execution_log) == 2
    assert len(executor.receipt_log) == 2
    assert plan.status == "interrupted"
    resumed = executor.execute(plan, approval)
    assert sum(r.status == "deduplicated" for r in resumed) == 2
    assert sum(r.status == "executed" for r in resumed) == 3
    assert len(tools.execution_log) == 5
    assert plan.status == "executed"


def test_event_operations_fixture_preserves_serious_money_with_generic_engine_and_card():
    from ripple.evaluation.matrix import event_operations_evidence
    evidence = event_operations_evidence()
    assert evidence.passed
    assert evidence.observed["net_preserved"] == 5180
    assert evidence.observed["av_choice"] == "move_av_delivery"
    assert evidence.observed["repair_card"] == "$5,800 at risk → $620 repair → $5,180 net preserved"
    assert evidence.observed["approval_cta"] == "Approve $620 repair"
    assert evidence.observed["top_impacts"] == [
        "Catering service window",
        "AV equipment delivery",
        "Security staffing coverage",
    ]
