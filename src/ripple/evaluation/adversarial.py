from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import List

from ripple.domain.models import Approval
from ripple.engine.dependency import DependencyEngine
from ripple.evaluation.matrix import (
    ScenarioEvidence,
    ambiguous_provider_evidence,
    content_drift_evidence,
    interruption_recovery_evidence,
    missed_deadline_evidence,
)
from ripple.golden import build_golden
from ripple.orchestration.executor import Executor
from ripple.orchestration.planner import Planner
from ripple.tools.simulated import ToolRegistry


def cost_scope_evidence() -> ScenarioEvidence:
    _, tools, planner, executor, change = build_golden()
    plan = planner.build_plan(change)
    approval = Approval(
        plan.id,
        plan.version,
        max_total_cost=41,
        external_people_notified=3,
        plan_snapshot_hash=plan.snapshot_hash(),
    )
    blocked = False
    try:
        executor.execute(plan, approval)
    except ValueError as exc:
        blocked = "cost exceeds approved" in str(exc)
    return ScenarioEvidence(
        "approval_cost_cap",
        blocked and not tools.execution_log,
        "execution fails closed when the plan exceeds the exact approved cost ceiling",
        {"blocked": blocked, "approved_max": 41, "plan_cost": plan.total_added_cost, "writes": len(tools.execution_log)},
    )


def notification_scope_evidence() -> ScenarioEvidence:
    _, tools, planner, executor, change = build_golden()
    plan = planner.build_plan(change)
    approval = Approval(
        plan.id,
        plan.version,
        max_total_cost=42,
        external_people_notified=2,
        plan_snapshot_hash=plan.snapshot_hash(),
    )
    blocked = False
    try:
        executor.execute(plan, approval)
    except ValueError as exc:
        blocked = "external notifications beyond approved scope" in str(exc)
    return ScenarioEvidence(
        "approval_people_cap",
        blocked and not tools.execution_log,
        "execution cannot silently notify more people than the user approved",
        {"blocked": blocked, "approved_people": 2, "plan_people": plan.external_people_notified, "writes": len(tools.execution_log)},
    )


def wrong_version_evidence() -> ScenarioEvidence:
    _, tools, planner, executor, change = build_golden()
    plan = planner.build_plan(change)
    approval = Approval(
        plan.id,
        plan.version + 1,
        max_total_cost=42,
        external_people_notified=3,
        plan_snapshot_hash=plan.snapshot_hash(),
    )
    blocked = False
    try:
        executor.execute(plan, approval)
    except ValueError as exc:
        blocked = "exact plan snapshot" in str(exc)
    return ScenarioEvidence(
        "wrong_plan_version",
        blocked and not tools.execution_log,
        "a stale or mismatched approval version authorizes zero writes",
        {"blocked": blocked, "approved_version": approval.plan_version, "plan_version": plan.version, "writes": len(tools.execution_log)},
    )


def provider_partial_failure_evidence() -> ScenarioEvidence:
    nodes, _, _, _, change = build_golden()
    tools = ToolRegistry(fail_operations={"extend_booking"})
    edges = [
        __import__("ripple.domain.models", fromlist=["DependencyEdge"]).DependencyEdge(
            "flight:return", nid, "arrival_dependency"
        )
        for nid in nodes
        if nid != "flight:return"
    ]
    plan = Planner(nodes, DependencyEngine(nodes, edges, tools)).build_plan(change)
    approval = Approval(plan.id, plan.version, 42, 3, plan.snapshot_hash())
    receipts = Executor(tools).execute(plan, approval)
    failed = [r for r in receipts if r.status == "failed"]
    passed = (
        plan.status == "partial"
        and sum(r.status == "executed" for r in receipts) == 4
        and len(failed) == 1
        and failed[0].result.get("error") == "simulated_provider_failure"
        and len(tools.execution_log) == 4
    )
    return ScenarioEvidence(
        "provider_partial_failure",
        passed,
        "a provider failure is reported as partial truth, never rewritten as success",
        {
            "plan_status": plan.status,
            "executed": sum(r.status == "executed" for r in receipts),
            "failed": len(failed),
            "unique_writes": len(tools.execution_log),
        },
    )


def run_adversarial_matrix() -> List[ScenarioEvidence]:
    # Reuse the established executable scenarios rather than maintaining a
    # second parallel safety framework. The extra cases below focus on the
    # approval boundary and truthful provider failure semantics.
    return [
        missed_deadline_evidence(),
        ambiguous_provider_evidence(),
        content_drift_evidence(),
        wrong_version_evidence(),
        cost_scope_evidence(),
        notification_scope_evidence(),
        provider_partial_failure_evidence(),
        interruption_recovery_evidence(),
    ]


def render_markdown(rows: List[ScenarioEvidence]) -> str:
    lines = [
        "# Ripple — Adversarial Failure Matrix",
        "",
        "Generated from executable scenarios. PASS means the observed behavior matched the fail-closed or truthful-degradation invariant; it does not mean every external provider failure mode is solved.",
        "",
        "| Failure / attack | Result | Required invariant | Observed |",
        "|---|---|---|---|",
    ]
    for row in rows:
        observed = "; ".join(f"{k}={v}" for k, v in row.observed.items()).replace("|", "/")
        lines.append(f"| `{row.scenario}` | {'PASS' if row.passed else 'FAIL'} | {row.invariant} | {observed} |")
    lines += [
        "",
        f"**Summary: {sum(row.passed for row in rows)}/{len(rows)} executable adversarial scenarios PASS.**",
        "",
        "## What this proves",
        "",
        "- approval drift, stale versions, cost expansion and notification-scope expansion produce zero writes;",
        "- ambiguous provider state blocks before execution;",
        "- missed repair windows remain unresolved instead of inventing a save;",
        "- provider failure remains a visible partial result;",
        "- interruption/retry reuses authoritative receipts and creates zero duplicate external writes.",
        "",
        "## What remains provider-dependent",
        "",
        "Exactly-once external effects still require the real provider to honor Ripple's idempotency key or expose an equivalent transactional primitive. Ripple's durable receipt boundary prevents replay of already-authoritative writes, but it cannot retroactively make a non-idempotent third-party API transactional.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    rows = run_adversarial_matrix()
    print(json.dumps([asdict(row) for row in rows], indent=2, default=str))
    repo_root = Path(__file__).resolve().parents[3]
    output = repo_root / "docs" / "ADVERSARIAL_FAILURE_MATRIX.md"
    output.write_text(render_markdown(rows), encoding="utf-8")
    print(f"Wrote {output}")
    if not all(row.passed for row in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
