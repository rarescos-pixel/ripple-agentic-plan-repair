import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from ripple.golden import build_golden
from ripple.domain.models import Approval
from ripple.tools.simulated import ToolRegistry
from ripple.engine.dependency import DependencyEngine
from ripple.orchestration.planner import Planner
from ripple.orchestration.executor import Executor


def test_cost_drift_requires_reapproval():
    nodes, tools, planner, executor, change = build_golden()
    plan = planner.build_plan(change)
    approval = Approval(plan.id, plan.version, max_total_cost=20, external_people_notified=3, plan_snapshot_hash=plan.snapshot_hash())
    with pytest.raises(ValueError, match="cost exceeds approved"):
        executor.execute(plan, approval)
    assert len(tools.execution_log) == 0


def test_wrong_plan_version_executes_nothing():
    nodes, tools, planner, executor, change = build_golden()
    plan = planner.build_plan(change)
    approval = Approval(plan.id, plan.version + 1, max_total_cost=42, external_people_notified=3, plan_snapshot_hash=plan.snapshot_hash())
    with pytest.raises(ValueError, match="exact plan snapshot"):
        executor.execute(plan, approval)
    assert len(tools.execution_log) == 0


def test_provider_failure_is_truthful_partial_result():
    nodes, _, _, _, change = build_golden()
    tools = ToolRegistry(fail_operations={"extend_booking"})
    engine = DependencyEngine(nodes, [
        __import__('ripple.domain.models', fromlist=['DependencyEdge']).DependencyEdge("flight:return", nid, "arrival_dependency")
        for nid in nodes if nid != "flight:return"
    ], tools)
    plan = Planner(nodes, engine).build_plan(change)
    approval = Approval(plan.id, plan.version, max_total_cost=42, external_people_notified=3, plan_snapshot_hash=plan.snapshot_hash())
    receipts = Executor(tools).execute(plan, approval)
    assert plan.status == "partial"
    assert sum(r.status == "executed" for r in receipts) == 4
    assert sum(r.status == "failed" for r in receipts) == 1
    failed = next(r for r in receipts if r.status == "failed")
    assert failed.result["error"] == "simulated_provider_failure"
    assert len(tools.execution_log) == 4


def test_snapshot_hash_includes_impact_content():
    from ripple.golden import build_golden
    from dataclasses import replace
    _, _, planner, _, change = build_golden()
    plan = planner.build_plan(change)
    before = plan.snapshot_hash()
    plan.impacts[0] = replace(plan.impacts[0], reason="tampered judge-visible impact reason")
    assert plan.snapshot_hash() != before
