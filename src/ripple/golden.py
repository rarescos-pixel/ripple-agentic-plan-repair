from ripple.aws.profile import validate_runtime_profile
from ripple.domain.models import PlanNode, NodeKind, DependencyEdge, ChangeEvent, Approval
from ripple.tools.simulated import ToolRegistry
from ripple.engine.dependency import DependencyEngine
from ripple.orchestration.planner import Planner
from ripple.orchestration.executor import Executor


def build_golden():
    # Validate deployment composition before constructing a state backend. In
    # production this prevents a partially-enabled AWS profile from creating an
    # executor/client before the runtime can fail closed.
    validate_runtime_profile()
    nodes = {
        "flight:return": PlanNode("flight:return", NodeKind.FACT, "Return flight"),
        "ride:R1": PlanNode("ride:R1", NodeKind.RIDE, "Airport pickup", start_at="2026-09-10T21:30:00", financial_exposure=38, attributes={"new_start_at":"2026-09-11T18:45:00","added_cost":0,"urgency":80}),
        "reservation:D1": PlanNode("reservation:D1", NodeKind.RESERVATION, "Dinner reservation", start_at="2026-09-10T20:00:00", financial_exposure=60, attributes={"deadline_minutes":18,"urgency":100}),
        "delivery:G1": PlanNode("delivery:G1", NodeKind.DELIVERY, "Grocery delivery", start_at="2026-09-11T08:00:00", financial_exposure=18, attributes={"new_start_at":"2026-09-11T20:00:00","urgency":60}),
        "care:C1": PlanNode("care:C1", NodeKind.CARE, "Pet care", end_at="2026-09-10T22:00:00", attributes={"new_end_at":"2026-09-11T20:00:00","added_cost":42,"urgency":90}),
        "calendar:M1": PlanNode("calendar:M1", NodeKind.CALENDAR, "Morning meeting", start_at="2026-09-11T09:00:00", external_people=3, attributes={"new_start_at":"2026-09-11T12:00:00","urgency":50}),
    }
    edges = [
        DependencyEdge("flight:return", "ride:R1", "arrival_dependency", condition="arrival_after_start"),
        DependencyEdge("flight:return", "reservation:D1", "arrival_dependency", condition="arrival_after_start"),
        DependencyEdge("flight:return", "delivery:G1", "arrival_dependency", condition="arrival_after_start"),
        DependencyEdge("flight:return", "care:C1", "arrival_dependency", condition="arrival_after_end"),
        DependencyEdge("flight:return", "calendar:M1", "arrival_dependency", condition="arrival_after_start"),
    ]
    change = ChangeEvent("change:flight-arrival-v1", "flight:return", "arrival_at", "2026-09-10T21:00:00", "2026-09-11T18:00:00")
    tools = ToolRegistry()
    engine = DependencyEngine(nodes, edges, tools)
    planner = Planner(nodes, engine)
    executor = Executor(tools)
    return nodes, tools, planner, executor, change


def run_golden():
    nodes, tools, planner, executor, change = build_golden()
    plan = planner.build_plan(change)
    approval = Approval(plan.id, plan.version, max_total_cost=42, external_people_notified=3, plan_snapshot_hash=plan.snapshot_hash())
    first = executor.execute(plan, approval)
    second = executor.execute(plan, approval)
    return plan, first, second, tools
