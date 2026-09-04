import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from ripple.domain.models import PlanNode, NodeKind, DependencyEdge, ChangeEvent
from ripple.tools.simulated import ToolRegistry
from ripple.engine.dependency import DependencyEngine
from ripple.orchestration.planner import Planner


def _plan_for_options(options):
    nodes = {
        "fact:change": PlanNode("fact:change", NodeKind.FACT, "Changed commitment"),
        "reservation:money": PlanNode(
            "reservation:money", NodeKind.RESERVATION, "High-value commitment",
            start_at="2026-09-10T12:00:00", financial_exposure=1000,
            attributes={"urgency": 100, "repair_options": options},
        ),
    }
    edges = [DependencyEdge("fact:change", "reservation:money", "time_dependency", condition="changed_time_after_start")]
    change = ChangeEvent("c", "fact:change", "start_at", "2026-09-10T10:00:00", "2026-09-10T18:00:00")
    return Planner(nodes, DependencyEngine(nodes, edges, ToolRegistry())).build_plan(change)


def test_planner_maximizes_net_cash_preserved_not_cheapest_sticker_price():
    plan = _plan_for_options([
        {"tool": "reservation", "operation": "cheap_save", "params": {}, "added_cost": 0, "avoidable_loss": 100},
        {"tool": "reservation", "operation": "high_value_save", "params": {}, "added_cost": 40, "avoidable_loss": 1000},
    ])
    assert plan.actions[0].operation == "high_value_save"
    assert plan.actions[0].avoidable_loss - plan.actions[0].added_cost == 960


def test_economic_tie_prefers_lower_cost_then_reversible():
    plan = _plan_for_options([
        {"tool": "reservation", "operation": "expensive", "params": {}, "added_cost": 50, "avoidable_loss": 150, "reversible": True},
        {"tool": "reservation", "operation": "cheap_irreversible", "params": {}, "added_cost": 20, "avoidable_loss": 120, "reversible": False},
        {"tool": "reservation", "operation": "cheap_reversible", "params": {}, "added_cost": 20, "avoidable_loss": 120, "reversible": True},
    ])
    assert plan.actions[0].operation == "cheap_reversible"
