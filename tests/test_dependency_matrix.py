import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from ripple.domain.models import PlanNode, NodeKind, DependencyEdge, ChangeEvent
from ripple.tools.simulated import ToolRegistry
from ripple.engine.dependency import DependencyEngine


def test_unaffected_commitment_is_not_repaired():
    nodes = {
        "flight:return": PlanNode("flight:return", NodeKind.FACT, "Return flight"),
        "dinner:late": PlanNode(
            "dinner:late", NodeKind.RESERVATION, "Late dinner",
            start_at="2026-09-11T20:30:00", financial_exposure=60,
            attributes={"deadline_minutes": 120, "urgency": 50},
        ),
    }
    edges = [DependencyEdge("flight:return", "dinner:late", "arrival_dependency", condition="arrival_after_start")]
    change = ChangeEvent("c", "flight:return", "arrival_at", "2026-09-10T21:00:00", "2026-09-11T18:00:00")
    impacts = DependencyEngine(nodes, edges, ToolRegistry()).detect_impacts(change)
    assert impacts == []


def test_two_step_dependency_path_is_preserved():
    nodes = {
        "flight:return": PlanNode("flight:return", NodeKind.FACT, "Return flight"),
        "home:presence": PlanNode("home:presence", NodeKind.FACT, "Presence at home"),
        "delivery:G1": PlanNode(
            "delivery:G1", NodeKind.DELIVERY, "Grocery delivery",
            start_at="2026-09-11T08:00:00", financial_exposure=18,
            attributes={"new_start_at":"2026-09-11T20:00:00", "urgency":60},
        ),
    }
    edges = [
        DependencyEdge("flight:return", "home:presence", "determines_presence", condition="always"),
        DependencyEdge("home:presence", "delivery:G1", "requires_presence", condition="arrival_after_start"),
    ]
    change = ChangeEvent("c", "flight:return", "arrival_at", "2026-09-10T21:00:00", "2026-09-11T18:00:00")
    impacts = DependencyEngine(nodes, edges, ToolRegistry()).detect_impacts(change)
    assert len(impacts) == 1
    assert impacts[0].dependency_path == ["flight:return", "home:presence", "delivery:G1"]


def test_generic_changed_time_alias_drives_non_flight_dependency():
    nodes = {
        "event:start": PlanNode("event:start", NodeKind.FACT, "Event start"),
        "delivery:gear": PlanNode(
            "delivery:gear", NodeKind.DELIVERY, "Equipment delivery",
            start_at="2026-10-10T14:00:00", financial_exposure=1200,
            attributes={"new_start_at": "2026-10-10T19:00:00", "urgency": 90},
        ),
    }
    edges = [DependencyEdge("event:start", "delivery:gear", "time_dependency", condition="changed_time_after_start")]
    change = ChangeEvent("event-change", "event:start", "start_at", "2026-10-10T12:00:00", "2026-10-10T18:00:00")
    impacts = DependencyEngine(nodes, edges, ToolRegistry()).detect_impacts(change)
    assert len(impacts) == 1
    assert impacts[0].affected_node_id == "delivery:gear"


def test_non_matching_path_does_not_suppress_later_valid_path():
    nodes = {
        "root": PlanNode("root", NodeKind.FACT, "Root change"),
        "early": PlanNode("early", NodeKind.FACT, "Early branch"),
        "late": PlanNode("late", NodeKind.FACT, "Late branch"),
        "delivery:x": PlanNode(
            "delivery:x", NodeKind.DELIVERY, "Critical delivery",
            start_at="2026-10-10T14:00:00", financial_exposure=500,
            attributes={"new_start_at": "2026-10-10T20:00:00", "urgency": 80},
        ),
    }
    edges = [
        DependencyEdge("root", "early", "branch", condition="always"),
        DependencyEdge("root", "late", "branch", condition="always"),
        DependencyEdge("early", "delivery:x", "time_dependency", condition="changed_time_after_end"),
        DependencyEdge("late", "delivery:x", "time_dependency", condition="changed_time_after_start"),
    ]
    nodes["delivery:x"] = PlanNode(
        "delivery:x", NodeKind.DELIVERY, "Critical delivery",
        start_at="2026-10-10T14:00:00", end_at="2026-10-10T22:00:00", financial_exposure=500,
        attributes={"new_start_at": "2026-10-10T20:00:00", "urgency": 80},
    )
    change = ChangeEvent("c", "root", "start_at", "2026-10-10T10:00:00", "2026-10-10T18:00:00")
    impacts = DependencyEngine(nodes, edges, ToolRegistry()).detect_impacts(change)
    assert len(impacts) == 1
    assert impacts[0].dependency_path == ["root", "late", "delivery:x"]
