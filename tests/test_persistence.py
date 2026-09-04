from __future__ import annotations

import pytest

from ripple.domain.models import Approval, ExecutionReceipt
from ripple.golden import build_golden
from ripple.orchestration.executor import Executor, SimulatedInterruption
from ripple.persistence import DynamoDbStateStore, SqliteStateStore
from ripple.tools.simulated import ToolRegistry


def test_sqlite_restart_resumes_without_duplicate_external_writes(tmp_path):
    _, tools_before, planner, _, change = build_golden()
    plan = planner.build_plan(change)
    approval = Approval(plan.id, plan.version, 42, 3, plan.snapshot_hash())
    path = tmp_path / "ripple-state.sqlite3"

    first_store = SqliteStateStore(path)
    first_executor = Executor(tools_before, first_store)
    with pytest.raises(SimulatedInterruption):
        first_executor.execute(plan, approval, interrupt_after=2)
    assert len(tools_before.execution_log) == 2

    second_store = SqliteStateStore(path)
    restored_approval = second_store.get_approval(plan.id, plan.snapshot_hash())
    assert restored_approval == approval

    tools_after = ToolRegistry()
    resumed = Executor(tools_after, second_store).execute(plan, restored_approval)
    assert sum(r.status == "deduplicated" for r in resumed) == 2
    assert sum(r.status == "executed" for r in resumed) == 3
    assert len(tools_before.execution_log) + len(tools_after.execution_log) == 5
    assert plan.status == "executed"


class ConditionalFailure(Exception):
    def __init__(self):
        self.response = {"Error": {"Code": "ConditionalCheckFailedException"}}
        super().__init__("conditional check failed")


class FakeDynamoDb:
    def __init__(self):
        self.items = {}
        self.conditional_failures = 0

    @staticmethod
    def _key(key):
        return key["pk"]["S"], key["sk"]["S"]

    def put_item(self, *, TableName, Item, ConditionExpression=None,
                 ExpressionAttributeNames=None, ExpressionAttributeValues=None):
        key = self._key(Item)
        current = self.items.get(key)
        if ConditionExpression and current and current.get("receipt_status", {}).get("S") == "executed":
            self.conditional_failures += 1
            raise ConditionalFailure()
        self.items[key] = Item
        return {}

    def get_item(self, *, TableName, Key, ConsistentRead):
        item = self.items.get(self._key(Key))
        return {"Item": item} if item else {}


def test_dynamodb_store_roundtrips_approval_and_authoritative_receipt():
    client = FakeDynamoDb()
    store = DynamoDbStateStore("ripple-state", client=client)
    approval = Approval("plan:1", 4, 25.0, 2, "snapshot-abc", actor="user")
    receipt = ExecutionReceipt("action:1", "idem-1", "executed", {"provider_id": "p-123"})

    store.save_approval("plan:1", approval)
    store.save_receipt("plan:1", receipt)
    assert store.get_approval("plan:1", "snapshot-abc") == approval
    assert store.get_receipt("idem-1") == receipt

    store.save_receipt("plan:1", ExecutionReceipt("action:1", "idem-1", "failed", {"error": "late"}))
    assert client.conditional_failures == 1
    assert store.get_receipt("idem-1") == receipt


def test_dynamodb_first_executed_receipt_wins_atomic_publication():
    client = FakeDynamoDb()
    a = DynamoDbStateStore("ripple-state", client=client)
    b = DynamoDbStateStore("ripple-state", client=client)
    first = ExecutionReceipt("action:A", "same-idem", "executed", {"provider_id": "first"})
    second = ExecutionReceipt("action:B", "same-idem", "executed", {"provider_id": "second"})

    a.save_receipt("plan:1", first)
    b.save_receipt("plan:1", second)

    assert client.conditional_failures == 1
    assert a.get_receipt("same-idem") == first
