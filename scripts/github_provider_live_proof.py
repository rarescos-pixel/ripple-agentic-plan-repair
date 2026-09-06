from __future__ import annotations

import os

from ripple.domain.models import Approval, RepairAction, RepairPlan
from ripple.orchestration.executor import Executor
from ripple.persistence import MemoryStateStore
from ripple.tools.github_issue import GitHubIssueProvider, GitHubIssueRegistry


def _plan(plan_id: str, action_id: str, idempotency_key: str, issue_number: int, body: str) -> RepairPlan:
    return RepairPlan(
        id=plan_id,
        version=1,
        source_change_event_id="provider-proof",
        impacts=[],
        actions=[
            RepairAction(
                id=action_id,
                tool="github_issue",
                operation="replace_issue_body",
                target_id=str(issue_number),
                params={"body": body},
                reversible=True,
                external_side_effect=True,
                added_cost=0,
                avoidable_loss=0,
                idempotency_key=idempotency_key,
            )
        ],
        total_added_cost=0,
        total_avoidable_loss=0,
        external_people_notified=0,
    )


def _approval(plan: RepairPlan) -> Approval:
    return Approval(
        plan_id=plan.id,
        plan_version=plan.version,
        max_total_cost=0,
        external_people_notified=0,
        plan_snapshot_hash=plan.snapshot_hash(),
        actor="integration-proof",
    )


def _execute_exact(registry: GitHubIssueRegistry, plan: RepairPlan, *, replay: bool = False):
    executor = Executor(registry, MemoryStateStore())
    first = executor.execute(plan, _approval(plan))
    if not replay:
        return first, []
    second = executor.execute(plan, _approval(plan))
    return first, second


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN", "")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    issue_number = int(os.environ.get("RIPPLE_PROVIDER_ISSUE", "42"))
    run_id = os.environ.get("RIPPLE_PROVIDER_RUN_ID", "manual")
    provider = GitHubIssueProvider(
        repository,
        token,
        allowed_issue_numbers={issue_number},
    )
    registry = GitHubIssueRegistry(provider)
    original = provider.get_issue_body(issue_number)
    if not original:
        raise RuntimeError("Provider proof fixture must have a non-empty baseline body")

    marker = (
        "Ripple real-provider proof in progress.\n\n"
        f"Run: {run_id}\n"
        "This temporary state is written by a bounded exact-approved Ripple plan and will be restored automatically."
    )
    write_plan = _plan(
        f"provider-proof:{run_id}:write",
        f"provider-proof:{run_id}:write-action",
        f"provider-proof:{run_id}:write-idem",
        issue_number,
        marker,
    )
    restore_plan = _plan(
        f"provider-proof:{run_id}:restore",
        f"provider-proof:{run_id}:restore-action",
        f"provider-proof:{run_id}:restore-idem",
        issue_number,
        original,
    )

    restored = False
    try:
        first, replay = _execute_exact(registry, write_plan, replay=True)
        if len(first) != 1 or first[0].status != "executed" or not first[0].result.get("verified"):
            raise RuntimeError("Real-provider write did not produce one verified executed receipt")
        if len(replay) != 1 or replay[0].status != "deduplicated":
            raise RuntimeError("Real-provider replay was not deduplicated by Ripple")
        if provider.get_issue_body(issue_number) != marker:
            raise RuntimeError("Real-provider state did not match the bounded write after readback")

        restored_receipts, _ = _execute_exact(registry, restore_plan)
        if len(restored_receipts) != 1 or restored_receipts[0].status not in {"executed", "deduplicated"}:
            raise RuntimeError("Real-provider restore did not complete")
        restored = provider.get_issue_body(issue_number) == original
        if not restored:
            raise RuntimeError("Real-provider fixture was not restored exactly")

        print("REAL_PROVIDER=GITHUB_ISSUES")
        print("REAL_PROVIDER_WRITE=PASS")
        print("REAL_PROVIDER_READBACK=PASS")
        print("REAL_PROVIDER_REPLAY_DEDUP=PASS")
        print("REAL_PROVIDER_RESTORE=PASS")
        print("REAL_PROVIDER_COST_USD=0")
        print("REAL_PROVIDER_PROOF=PASS")
    finally:
        # Safety cleanup is itself another bounded exact-approved Ripple plan.
        # This runs only if the normal restoration did not already succeed.
        if not restored:
            try:
                if provider.get_issue_body(issue_number) != original:
                    _execute_exact(registry, restore_plan)
            except Exception:
                # Preserve the original proof exception while allowing the
                # workflow to surface a failed cleanup state through GitHub.
                print("REAL_PROVIDER_EMERGENCY_RESTORE=FAILED")


if __name__ == "__main__":
    main()
