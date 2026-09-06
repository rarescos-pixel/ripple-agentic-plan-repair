from __future__ import annotations

import pytest

from ripple.domain.models import Approval, RepairAction, RepairPlan
from ripple.orchestration.executor import Executor
from ripple.persistence import MemoryStateStore
from ripple.tools.github_issue import GitHubIssueProvider, GitHubIssueRegistry


class FakeTransport:
    def __init__(self, body: str = "baseline") -> None:
        self.body = body
        self.calls: list[tuple[str, str, dict | None]] = []

    def __call__(self, method: str, path: str, payload: dict | None):
        self.calls.append((method, path, payload))
        if method == "GET":
            return {"body": self.body}
        if method == "PATCH":
            self.body = str(payload["body"])
            return {"body": self.body}
        raise AssertionError(method)


def _action(*, issue: int = 42, body: str = "changed") -> RepairAction:
    return RepairAction(
        id="a1",
        tool="github_issue",
        operation="replace_issue_body",
        target_id=str(issue),
        params={"body": body},
        reversible=True,
        external_side_effect=True,
        added_cost=0,
        avoidable_loss=0,
        idempotency_key="idem-1",
    )


def _plan(action: RepairAction) -> RepairPlan:
    return RepairPlan(
        id="p1",
        version=1,
        source_change_event_id="provider-proof",
        impacts=[],
        actions=[action],
        total_added_cost=0,
        total_avoidable_loss=0,
        external_people_notified=0,
    )


def _approval(plan: RepairPlan) -> Approval:
    return Approval(plan.id, plan.version, 0, 0, plan.snapshot_hash(), actor="test")


def test_real_provider_registry_is_narrow_and_reversible():
    fake = FakeTransport()
    provider = GitHubIssueProvider(
        "owner/repo", "token", allowed_issue_numbers={42}, transport=fake
    )
    registry = GitHubIssueRegistry(provider)
    action = _action()
    registry.preflight(action)

    with pytest.raises(ValueError, match="allowlist"):
        registry.preflight(_action(issue=43))

    wrong_tool = _action()
    wrong_tool.tool = "calendar"
    with pytest.raises(ValueError, match="outside"):
        registry.preflight(wrong_tool)

    costly = _action()
    costly.added_cost = 1
    with pytest.raises(ValueError, match="cost"):
        registry.preflight(costly)

    irreversible = _action()
    irreversible.reversible = False
    with pytest.raises(ValueError, match="reversible"):
        registry.preflight(irreversible)


def test_executor_real_provider_contract_writes_once_and_replay_deduplicates():
    fake = FakeTransport()
    provider = GitHubIssueProvider(
        "owner/repo", "token", allowed_issue_numbers={42}, transport=fake
    )
    registry = GitHubIssueRegistry(provider)
    plan = _plan(_action(body="new bounded body"))
    executor = Executor(registry, MemoryStateStore())

    first = executor.execute(plan, _approval(plan))
    assert len(first) == 1
    assert first[0].status == "executed"
    assert first[0].result["verified"] is True
    assert fake.body == "new bounded body"
    assert [c[0] for c in fake.calls] == ["GET", "PATCH", "GET"]

    replay = executor.execute(plan, _approval(plan))
    assert len(replay) == 1
    assert replay[0].status == "deduplicated"
    assert [c[0] for c in fake.calls] == ["GET", "PATCH", "GET"]


def test_provider_fails_closed_when_post_write_state_is_ambiguous():
    state = {"body": "baseline"}

    def ambiguous(method: str, path: str, payload: dict | None):
        if method == "GET":
            return {"body": state["body"]}
        if method == "PATCH":
            return {"body": "something-else"}
        raise AssertionError(method)

    provider = GitHubIssueProvider(
        "owner/repo", "token", allowed_issue_numbers={42}, transport=ambiguous
    )
    with pytest.raises(RuntimeError, match="ambiguous"):
        provider.replace_issue_body(_action(body="expected"))


def test_provider_receipts_never_include_issue_body_content():
    fake = FakeTransport(body="private baseline text")
    provider = GitHubIssueProvider(
        "owner/repo", "token", allowed_issue_numbers={42}, transport=fake
    )
    receipt = provider.replace_issue_body(_action(body="private changed text"))
    rendered = repr(receipt.result)
    assert "private baseline text" not in rendered
    assert "private changed text" not in rendered
    assert "before_body_sha256" in receipt.result
    assert "after_body_sha256" in receipt.result
