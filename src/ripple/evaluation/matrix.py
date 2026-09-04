from __future__ import annotations
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Dict, List

from ripple.domain.models import PlanNode, NodeKind, DependencyEdge, ChangeEvent, Approval
from ripple.engine.dependency import DependencyEngine
from ripple.golden import build_golden
from ripple.orchestration.executor import Executor, SimulatedInterruption
from ripple.orchestration.planner import Planner
from ripple.presentation import build_repair_card
from ripple.tools.simulated import ToolRegistry


@dataclass(frozen=True)
class ScenarioEvidence:
    scenario: str
    passed: bool
    invariant: str
    observed: Dict[str, Any]


def golden_evidence() -> ScenarioEvidence:
    _, tools, planner, executor, change = build_golden()
    plan = planner.build_plan(change)
    approval = Approval(plan.id, plan.version, 42, 3, plan.snapshot_hash())
    receipts = executor.execute(plan, approval)
    passed = (
        len(plan.impacts) == 5 and len(plan.actions) == 5 and
        plan.total_added_cost == 42 and plan.total_avoidable_loss == 116 and
        plan.net_direct_cash_preserved == 74 and
        sum(r.status == "executed" for r in receipts) == 5
    )
    return ScenarioEvidence("golden_flight_cascade", passed, "one change repairs five bounded commitments", {
        "impacts": len(plan.impacts), "actions": len(plan.actions), "added_cost": plan.total_added_cost,
        "avoidable_loss": plan.total_avoidable_loss, "net_preserved": plan.net_direct_cash_preserved,
        "writes": len(tools.execution_log), "snapshot_hash_prefix": plan.snapshot_hash()[:12],
    })


def missed_deadline_evidence() -> ScenarioEvidence:
    nodes = {
        "flight:return": PlanNode("flight:return", NodeKind.FACT, "Return flight"),
        "reservation:D1": PlanNode("reservation:D1", NodeKind.RESERVATION, "Dinner reservation",
            start_at="2026-09-10T20:00:00", financial_exposure=60,
            attributes={"deadline_missed": True, "deadline_minutes": -5, "urgency": 100}),
    }
    tools = ToolRegistry()
    plan = Planner(nodes, DependencyEngine(nodes, [DependencyEdge("flight:return", "reservation:D1", "arrival_dependency", condition="arrival_after_start")], tools)).build_plan(
        ChangeEvent("c", "flight:return", "arrival_at", "2026-09-10T18:00:00", "2026-09-11T18:00:00")
    )
    passed = len(plan.impacts) == 1 and not plan.actions and plan.unresolved_items == ["reservation:D1"] and not tools.execution_log
    return ScenarioEvidence("missed_deadline", passed, "expired repair windows remain visible; no fabricated save", {
        "impacts": len(plan.impacts), "actions": len(plan.actions), "unresolved": plan.unresolved_items, "writes": len(tools.execution_log),
    })


def ambiguous_provider_evidence() -> ScenarioEvidence:
    nodes, _, _, _, change = build_golden()
    tools = ToolRegistry(ambiguous_operations={"reschedule_delivery"})
    edges = [DependencyEdge("flight:return", nid, "arrival_dependency") for nid in nodes if nid != "flight:return"]
    plan = Planner(nodes, DependencyEngine(nodes, edges, tools)).build_plan(change)
    approval = Approval(plan.id, plan.version, 42, 3, plan.snapshot_hash())
    blocked = False
    try:
        Executor(tools).execute(plan, approval)
    except ValueError as exc:
        blocked = "Provider state ambiguous" in str(exc)
    return ScenarioEvidence("ambiguous_provider", blocked and not tools.execution_log, "ambiguous provider state blocks the whole plan before writes", {
        "blocked": blocked, "writes": len(tools.execution_log),
    })


def hard_preference_evidence() -> ScenarioEvidence:
    nodes = {
        "flight:return": PlanNode("flight:return", NodeKind.FACT, "Return flight"),
        "reservation:D1": PlanNode("reservation:D1", NodeKind.RESERVATION, "Anniversary dinner",
            start_at="2026-09-10T20:00:00", financial_exposure=100,
            attributes={"deadline_minutes": 30, "new_start_at": "2026-09-11T20:00:00", "reschedule_cost": 25,
                        "disallowed_operations": ["cancel_reservation"], "urgency": 90}),
    }
    plan = Planner(nodes, DependencyEngine(nodes, [DependencyEdge("flight:return", "reservation:D1", "arrival_dependency", condition="arrival_after_start")], ToolRegistry())).build_plan(
        ChangeEvent("c", "flight:return", "arrival_at", "2026-09-10T18:00:00", "2026-09-11T18:00:00")
    )
    action = plan.actions[0]
    passed = action.operation == "reschedule_reservation" and action.added_cost == 25
    return ScenarioEvidence("hard_preference", passed, "explicit hard constraints filter options before cost optimization", {
        "selected_operation": action.operation, "added_cost": action.added_cost,
    })


def event_operations_evidence() -> ScenarioEvidence:
    """A non-flight, money-heavy fixture proving the engine and decision surface are not travel-hardcoded."""
    nodes = {
        "event:start": PlanNode("event:start", NodeKind.FACT, "Conference start time"),
        "delivery:av": PlanNode(
            "delivery:av", NodeKind.DELIVERY, "AV equipment delivery",
            start_at="2026-10-10T14:00:00", financial_exposure=1200,
            attributes={
                "urgency": 95,
                "repair_options": [
                    {"tool": "delivery", "operation": "move_av_delivery", "params": {"new_start_at": "2026-10-10T19:00:00"}, "added_cost": 140, "avoidable_loss": 1200, "reversible": True},
                    {"tool": "delivery", "operation": "abandon_av_slot", "params": {}, "added_cost": 0, "avoidable_loss": 100, "reversible": False},
                ],
            },
        ),
        "reservation:catering": PlanNode(
            "reservation:catering", NodeKind.RESERVATION, "Catering service window",
            start_at="2026-10-10T15:00:00", financial_exposure=2500,
            attributes={"urgency": 100, "repair_options": [
                {"tool": "reservation", "operation": "reschedule_catering", "params": {"new_start_at": "2026-10-10T19:30:00"}, "added_cost": 180, "avoidable_loss": 2500, "reversible": True}
            ]},
        ),
        "ride:vip": PlanNode(
            "ride:vip", NodeKind.RIDE, "VIP transport",
            start_at="2026-10-10T16:00:00", financial_exposure=600,
            attributes={"urgency": 85, "repair_options": [
                {"tool": "ride", "operation": "move_vip_transport", "params": {"new_start_at": "2026-10-10T19:15:00"}, "added_cost": 80, "avoidable_loss": 600, "reversible": True}
            ]},
        ),
        "care:security": PlanNode(
            "care:security", NodeKind.CARE, "Security staffing coverage",
            end_at="2026-10-10T17:00:00", financial_exposure=1500,
            attributes={"urgency": 90, "repair_options": [
                {"tool": "care", "operation": "extend_security_staffing", "params": {"new_end_at": "2026-10-10T23:00:00"}, "added_cost": 220, "avoidable_loss": 1500, "reversible": True}
            ]},
        ),
        "calendar:sponsors": PlanNode(
            "calendar:sponsors", NodeKind.CALENDAR, "Sponsor briefing",
            start_at="2026-10-10T16:30:00", external_people=8,
            attributes={"urgency": 70, "repair_options": [
                {"tool": "calendar", "operation": "move_sponsor_briefing", "params": {"new_start_at": "2026-10-10T20:00:00", "notify_attendees": True}, "added_cost": 0, "avoidable_loss": 0, "reversible": True}
            ]},
        ),
    }
    edges = [
        DependencyEdge("event:start", "delivery:av", "time_dependency", condition="changed_time_after_start"),
        DependencyEdge("event:start", "reservation:catering", "time_dependency", condition="changed_time_after_start"),
        DependencyEdge("event:start", "ride:vip", "time_dependency", condition="changed_time_after_start"),
        DependencyEdge("event:start", "care:security", "coverage_dependency", condition="changed_time_after_end"),
        DependencyEdge("event:start", "calendar:sponsors", "time_dependency", condition="changed_time_after_start"),
    ]
    tools = ToolRegistry()
    change = ChangeEvent("change:event-delay-v1", "event:start", "start_at", "2026-10-10T12:00:00", "2026-10-10T18:00:00")
    plan = Planner(nodes, DependencyEngine(nodes, edges, tools)).build_plan(change)
    card = build_repair_card(plan)
    selected = {a.target_id: a.operation for a in plan.actions}
    top_labels = [impact["label"] for impact in card["top_impacts"]]
    passed = (
        len(plan.impacts) == 5 and len(plan.actions) == 5
        and plan.total_added_cost == 620
        and plan.total_avoidable_loss == 5800
        and plan.net_direct_cash_preserved == 5180
        and selected["delivery:av"] == "move_av_delivery"
        and plan.external_people_notified == 8
        and card["money_summary"] == "$5,800 at risk → $620 repair → $5,180 net preserved"
        and card["decision"]["label"] == "Approve $620 repair"
        and top_labels == ["Catering service window", "AV equipment delivery", "Security staffing coverage"]
    )
    return ScenarioEvidence(
        "event_operations_cascade", passed,
        "generic changed-time graph and Alexa decision surface preserve the most net cash outside travel",
        {
            "impacts": len(plan.impacts), "actions": len(plan.actions),
            "added_cost": plan.total_added_cost, "avoidable_loss": plan.total_avoidable_loss,
            "net_preserved": plan.net_direct_cash_preserved, "external_people": plan.external_people_notified,
            "av_choice": selected.get("delivery:av"),
            "repair_card": card["money_summary"], "approval_cta": card["decision"]["label"],
            "top_impacts": top_labels,
        },
    )


def content_drift_evidence() -> ScenarioEvidence:
    _, tools, planner, executor, change = build_golden()
    plan = planner.build_plan(change)
    approval = Approval(plan.id, plan.version, 42, 3, plan.snapshot_hash())
    original_hash = approval.plan_snapshot_hash
    plan.actions[0].params["new_start_at"] = "2026-09-11T19:30:00"
    blocked = False
    try:
        executor.execute(plan, approval)
    except ValueError as exc:
        blocked = "content drifted" in str(exc)
    return ScenarioEvidence("content_drift", blocked and not tools.execution_log, "approval binds to exact content, not only a version integer", {
        "blocked": blocked, "writes": len(tools.execution_log), "hash_changed": original_hash != plan.snapshot_hash(),
    })


def interruption_recovery_evidence() -> ScenarioEvidence:
    _, tools, planner, executor, change = build_golden()
    plan = planner.build_plan(change)
    approval = Approval(plan.id, plan.version, 42, 3, plan.snapshot_hash())
    interrupted = False
    try:
        executor.execute(plan, approval, interrupt_after=2)
    except SimulatedInterruption:
        interrupted = True
    persisted_before_resume = len(executor.receipt_log)
    resumed = executor.execute(plan, approval)
    passed = (
        interrupted and persisted_before_resume == 2 and
        sum(r.status == "deduplicated" for r in resumed) == 2 and
        sum(r.status == "executed" for r in resumed) == 3 and
        len(tools.execution_log) == 5 and plan.status == "executed"
    )
    return ScenarioEvidence("interruption_recovery", passed, "resume after interruption produces zero duplicate external writes", {
        "persisted_receipts_before_resume": persisted_before_resume,
        "deduplicated_on_resume": sum(r.status == "deduplicated" for r in resumed),
        "new_writes_on_resume": sum(r.status == "executed" for r in resumed),
        "unique_writes_total": len(tools.execution_log), "final_status": plan.status,
    })


def run_matrix() -> List[ScenarioEvidence]:
    return [
        golden_evidence(), missed_deadline_evidence(), ambiguous_provider_evidence(),
        hard_preference_evidence(), event_operations_evidence(), content_drift_evidence(), interruption_recovery_evidence(),
    ]


def render_markdown(rows: List[ScenarioEvidence]) -> str:
    lines = [
        "# Ripple — Evidence Matrix v1.3", "",
        "This report is generated from executable scenarios. It is evidence, not marketing copy.", "",
        "| Scenario | Result | Invariant | Observed |", "|---|---|---|---|",
    ]
    for r in rows:
        observed = "; ".join(f"{k}={v}" for k, v in r.observed.items()).replace("|", "/")
        lines.append(f"| `{r.scenario}` | {'PASS' if r.passed else 'FAIL'} | {r.invariant} | {observed} |")
    lines += ["", f"**Summary: {sum(r.passed for r in rows)}/{len(rows)} scenarios PASS.**", ""]
    return "\n".join(lines)


def main() -> None:
    rows = run_matrix()
    print(json.dumps([asdict(r) for r in rows], indent=2))
    report = render_markdown(rows)
    repo_root = Path(__file__).resolve().parents[3]
    out = repo_root / "docs" / "EVIDENCE_MATRIX.md"
    out.write_text(report, encoding="utf-8")
    print(f"Wrote {out}")
    if not all(r.passed for r in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
