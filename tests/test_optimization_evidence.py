from ripple.domain.models import ChangeEvent, DependencyEdge, NodeKind, PlanNode
from ripple.engine.dependency import DependencyEngine
from ripple.orchestration.planner import Planner
from ripple.presentation import build_repair_card
from ripple.tools.simulated import ToolRegistry


def test_repair_card_explains_provable_net_value_choice():
    nodes = {
        "event:start": PlanNode("event:start", NodeKind.FACT, "Conference start time"),
        "delivery:av": PlanNode(
            "delivery:av",
            NodeKind.DELIVERY,
            "AV equipment delivery",
            start_at="2026-10-10T14:00:00",
            financial_exposure=1200,
            attributes={
                "repair_options": [
                    {
                        "tool": "delivery",
                        "operation": "move_av_delivery",
                        "params": {"new_start_at": "2026-10-10T19:00:00"},
                        "added_cost": 140,
                        "avoidable_loss": 1200,
                        "reversible": True,
                    },
                    {
                        "tool": "delivery",
                        "operation": "abandon_av_slot",
                        "params": {},
                        "added_cost": 0,
                        "avoidable_loss": 100,
                        "reversible": False,
                    },
                ]
            },
        ),
    }
    tools = ToolRegistry()
    engine = DependencyEngine(
        nodes,
        [DependencyEdge("event:start", "delivery:av", "time_dependency", condition="changed_time_after_start")],
        tools,
    )
    plan = Planner(nodes, engine).build_plan(
        ChangeEvent(
            "change:event-delay",
            "event:start",
            "start_at",
            "2026-10-10T12:00:00",
            "2026-10-10T18:00:00",
        )
    )
    card = build_repair_card(plan)
    evidence = card["optimization_evidence"]

    assert len(evidence) == 1
    choice = evidence[0]
    assert choice["commitment"] == "AV equipment delivery"
    assert choice["selected_operation"] == "move_av_delivery"
    assert choice["selected_net_preserved"] == 1060
    assert choice["best_alternative_operation"] == "abandon_av_slot"
    assert choice["best_alternative_net_preserved"] == 100
    assert choice["net_advantage"] == 960


def test_repair_card_does_not_invent_reason_when_policy_filter_is_hidden():
    nodes = {
        "flight:return": PlanNode("flight:return", NodeKind.FACT, "Return flight"),
        "reservation:D1": PlanNode(
            "reservation:D1",
            NodeKind.RESERVATION,
            "Anniversary dinner",
            start_at="2026-09-10T20:00:00",
            financial_exposure=100,
            attributes={
                "new_start_at": "2026-09-11T20:00:00",
                "reschedule_cost": 25,
                "disallowed_operations": ["cancel_reservation"],
            },
        ),
    }
    tools = ToolRegistry()
    engine = DependencyEngine(
        nodes,
        [DependencyEdge("flight:return", "reservation:D1", "arrival_dependency", condition="arrival_after_start")],
        tools,
    )
    plan = Planner(nodes, engine).build_plan(
        ChangeEvent(
            "change:flight",
            "flight:return",
            "arrival_at",
            "2026-09-10T18:00:00",
            "2026-09-11T18:00:00",
        )
    )

    assert plan.actions[0].operation == "reschedule_reservation"
    assert build_repair_card(plan)["optimization_evidence"] == []
