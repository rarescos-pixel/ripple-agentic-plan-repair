from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Protocol

from ripple.domain.models import (
    ActionStatus,
    Approval,
    ChangeEvent,
    ExecutionReceipt,
    Impact,
    ImpactStatus,
    RepairAction,
    RepairOption,
    RepairPlan,
)


@dataclass(frozen=True)
class PersistedProposal:
    """Content-addressed proposal needed to resume an exact approved plan.

    The owner subject is stored alongside the snapshot so a different MCP
    principal cannot recover another user's approved authority merely by
    learning a plan id/hash pair.
    """

    plan: RepairPlan
    change: ChangeEvent
    owner_subject: str


class StateStore(Protocol):
    def save_proposal(self, plan: RepairPlan, change: ChangeEvent, owner_subject: str) -> None: ...
    def get_proposal(self, plan_id: str, snapshot_hash: str) -> PersistedProposal | None: ...
    def save_approval(self, plan_id: str, approval: Approval) -> None: ...
    def get_approval(self, plan_id: str, snapshot_hash: str) -> Approval | None: ...
    def save_receipt(self, plan_id: str, receipt: ExecutionReceipt) -> None: ...
    def get_receipt(self, idempotency_key: str) -> ExecutionReceipt | None: ...


def _approval_from(payload: dict[str, Any]) -> Approval:
    return Approval(
        plan_id=str(payload["plan_id"]),
        plan_version=int(payload["plan_version"]),
        max_total_cost=float(payload["max_total_cost"]),
        external_people_notified=int(payload["external_people_notified"]),
        plan_snapshot_hash=str(payload["plan_snapshot_hash"]),
        actor=str(payload.get("actor", "user")),
    )


def _receipt_from(payload: dict[str, Any]) -> ExecutionReceipt:
    return ExecutionReceipt(
        action_id=str(payload["action_id"]),
        idempotency_key=str(payload["idempotency_key"]),
        status=str(payload["status"]),
        result=dict(payload.get("result") or {}),
        attempt=int(payload.get("attempt", 1)),
    )


def _option_from(payload: dict[str, Any]) -> RepairOption:
    return RepairOption(
        tool=str(payload["tool"]),
        operation=str(payload["operation"]),
        params=dict(payload.get("params") or {}),
        added_cost=float(payload.get("added_cost", 0)),
        avoidable_loss=float(payload.get("avoidable_loss", 0)),
        reversible=bool(payload.get("reversible", True)),
        external_side_effect=bool(payload.get("external_side_effect", True)),
    )


def _impact_from(payload: dict[str, Any]) -> Impact:
    return Impact(
        affected_node_id=str(payload["affected_node_id"]),
        dependency_path=[str(x) for x in payload.get("dependency_path") or []],
        reason=str(payload["reason"]),
        status=ImpactStatus(str(payload["status"])),
        direct_cash_at_risk=float(payload.get("direct_cash_at_risk", 0)),
        urgency=int(payload.get("urgency", 0)),
        options=[_option_from(x) for x in payload.get("options") or []],
    )


def _action_from(payload: dict[str, Any]) -> RepairAction:
    return RepairAction(
        id=str(payload["id"]),
        tool=str(payload["tool"]),
        operation=str(payload["operation"]),
        target_id=str(payload["target_id"]),
        params=dict(payload.get("params") or {}),
        reversible=bool(payload.get("reversible", True)),
        external_side_effect=bool(payload.get("external_side_effect", True)),
        added_cost=float(payload.get("added_cost", 0)),
        avoidable_loss=float(payload.get("avoidable_loss", 0)),
        idempotency_key=str(payload["idempotency_key"]),
        approval_level=str(payload.get("approval_level", "explicit_plan")),
        status=ActionStatus(str(payload.get("status", ActionStatus.PROPOSED.value))),
    )


def _plan_from(payload: dict[str, Any]) -> RepairPlan:
    return RepairPlan(
        id=str(payload["id"]),
        version=int(payload["version"]),
        source_change_event_id=str(payload["source_change_event_id"]),
        impacts=[_impact_from(x) for x in payload.get("impacts") or []],
        actions=[_action_from(x) for x in payload.get("actions") or []],
        total_added_cost=float(payload.get("total_added_cost", 0)),
        total_avoidable_loss=float(payload.get("total_avoidable_loss", 0)),
        external_people_notified=int(payload.get("external_people_notified", 0)),
        unresolved_items=[str(x) for x in payload.get("unresolved_items") or []],
        status=str(payload.get("status", "proposed")),
    )


def _change_from(payload: dict[str, Any]) -> ChangeEvent:
    return ChangeEvent(
        id=str(payload["id"]),
        node_id=str(payload["node_id"]),
        field=str(payload["field"]),
        old_value=payload.get("old_value"),
        new_value=payload.get("new_value"),
        source=str(payload.get("source", "voice")),
        confidence=float(payload.get("confidence", 1.0)),
        correlation_id=str(payload.get("correlation_id", "golden")),
    )


def _proposal_json(plan: RepairPlan, change: ChangeEvent, owner_subject: str) -> str:
    if not owner_subject:
        raise ValueError("owner_subject is required for durable proposal recovery")
    if change.id != plan.source_change_event_id:
        raise ValueError("proposal change does not match plan source event")
    return json.dumps(
        {"plan": asdict(plan), "change": asdict(change), "owner_subject": owner_subject},
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _proposal_from(payload: dict[str, Any], expected_hash: str) -> PersistedProposal:
    plan = _plan_from(dict(payload["plan"]))
    change = _change_from(dict(payload["change"]))
    owner_subject = str(payload["owner_subject"])
    if not owner_subject:
        raise ValueError("persisted proposal has no owner subject")
    if change.id != plan.source_change_event_id:
        raise ValueError("persisted proposal source event mismatch")
    if plan.snapshot_hash() != expected_hash:
        raise ValueError("persisted proposal content hash mismatch")
    return PersistedProposal(plan=plan, change=change, owner_subject=owner_subject)


class MemoryStateStore:
    def __init__(self) -> None:
        self.proposals: dict[tuple[str, str], PersistedProposal] = {}
        self.approvals: dict[tuple[str, str], Approval] = {}
        self.receipts: dict[str, ExecutionReceipt] = {}

    def save_proposal(self, plan: RepairPlan, change: ChangeEvent, owner_subject: str) -> None:
        snapshot_hash = plan.snapshot_hash()
        payload = json.loads(_proposal_json(plan, change, owner_subject))
        self.proposals[(plan.id, snapshot_hash)] = _proposal_from(payload, snapshot_hash)

    def get_proposal(self, plan_id: str, snapshot_hash: str) -> PersistedProposal | None:
        return self.proposals.get((plan_id, snapshot_hash))

    def save_approval(self, plan_id: str, approval: Approval) -> None:
        self.approvals[(plan_id, approval.plan_snapshot_hash)] = approval

    def get_approval(self, plan_id: str, snapshot_hash: str) -> Approval | None:
        return self.approvals.get((plan_id, snapshot_hash))

    def save_receipt(self, plan_id: str, receipt: ExecutionReceipt) -> None:
        current = self.receipts.get(receipt.idempotency_key)
        if current is not None and current.status == "executed":
            return
        self.receipts[receipt.idempotency_key] = receipt

    def get_receipt(self, idempotency_key: str) -> ExecutionReceipt | None:
        return self.receipts.get(idempotency_key)


class SqliteStateStore:
    """Small durable local backend used for restart tests and offline demos.

    SQLite is not the production target. It exists so durability semantics are
    executable without requiring an AWS account. DynamoDB implements the same
    contract for deployment.
    """

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self.path = str(path)
        parent = Path(self.path).expanduser().resolve().parent
        parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS proposals ("
                "plan_id TEXT NOT NULL, snapshot_hash TEXT NOT NULL, payload TEXT NOT NULL, "
                "PRIMARY KEY(plan_id, snapshot_hash))"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS approvals ("
                "plan_id TEXT NOT NULL, snapshot_hash TEXT NOT NULL, payload TEXT NOT NULL, "
                "PRIMARY KEY(plan_id, snapshot_hash))"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS receipts ("
                "idempotency_key TEXT PRIMARY KEY, plan_id TEXT NOT NULL, payload TEXT NOT NULL)"
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def save_proposal(self, plan: RepairPlan, change: ChangeEvent, owner_subject: str) -> None:
        snapshot_hash = plan.snapshot_hash()
        payload = _proposal_json(plan, change, owner_subject)
        with self._connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO proposals(plan_id, snapshot_hash, payload) VALUES (?, ?, ?)",
                (plan.id, snapshot_hash, payload),
            )

    def get_proposal(self, plan_id: str, snapshot_hash: str) -> PersistedProposal | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT payload FROM proposals WHERE plan_id=? AND snapshot_hash=?",
                (plan_id, snapshot_hash),
            ).fetchone()
        return _proposal_from(json.loads(row[0]), snapshot_hash) if row else None

    def save_approval(self, plan_id: str, approval: Approval) -> None:
        payload = json.dumps(asdict(approval), sort_keys=True, separators=(",", ":"))
        with self._connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO approvals(plan_id, snapshot_hash, payload) VALUES (?, ?, ?)",
                (plan_id, approval.plan_snapshot_hash, payload),
            )

    def get_approval(self, plan_id: str, snapshot_hash: str) -> Approval | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT payload FROM approvals WHERE plan_id=? AND snapshot_hash=?",
                (plan_id, snapshot_hash),
            ).fetchone()
        return _approval_from(json.loads(row[0])) if row else None

    def save_receipt(self, plan_id: str, receipt: ExecutionReceipt) -> None:
        current = self.get_receipt(receipt.idempotency_key)
        if current is not None and current.status == "executed":
            return
        payload = json.dumps(asdict(receipt), sort_keys=True, separators=(",", ":"), default=str)
        with self._connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO receipts(idempotency_key, plan_id, payload) VALUES (?, ?, ?)",
                (receipt.idempotency_key, plan_id, payload),
            )

    def get_receipt(self, idempotency_key: str) -> ExecutionReceipt | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT payload FROM receipts WHERE idempotency_key=?",
                (idempotency_key,),
            ).fetchone()
        return _receipt_from(json.loads(row[0])) if row else None


class DynamoDbStateStore:
    """Single-table proposal/approval/idempotency store.

    boto3 is imported lazily so local development and CI need no AWS SDK unless
    the DynamoDB backend is explicitly selected. A client can be injected for
    deterministic tests.

    Receipt publication is atomic: once an `executed` receipt wins for an
    idempotency key, no concurrent or later attempt may overwrite it. Provider
    calls still carry the same idempotency key; true exactly-once effects also
    require the provider to honor that key or expose an equivalent transaction
    primitive.
    """

    def __init__(self, table_name: str, *, client: Any = None, region_name: str | None = None) -> None:
        self.table_name = table_name
        if client is None:
            try:
                import boto3  # type: ignore
            except ImportError as exc:  # pragma: no cover - only used in live AWS mode
                raise RuntimeError("boto3 is required for RIPPLE_STATE_BACKEND=dynamodb") from exc
            client = boto3.client("dynamodb", region_name=region_name)
        self.client = client

    @staticmethod
    def _proposal_key(plan_id: str, snapshot_hash: str) -> dict[str, dict[str, str]]:
        return {
            "pk": {"S": f"PLAN#{plan_id}"},
            "sk": {"S": f"PROPOSAL#{snapshot_hash}"},
        }

    @staticmethod
    def _approval_key(plan_id: str, snapshot_hash: str) -> dict[str, dict[str, str]]:
        return {
            "pk": {"S": f"PLAN#{plan_id}"},
            "sk": {"S": f"APPROVAL#{snapshot_hash}"},
        }

    @staticmethod
    def _receipt_key(idempotency_key: str) -> dict[str, dict[str, str]]:
        return {
            "pk": {"S": f"IDEMPOTENCY#{idempotency_key}"},
            "sk": {"S": "RECEIPT"},
        }

    @staticmethod
    def _is_conditional_failure(exc: Exception) -> bool:
        response = getattr(exc, "response", None)
        if not isinstance(response, dict):
            return False
        error = response.get("Error") or {}
        return error.get("Code") == "ConditionalCheckFailedException"

    def save_proposal(self, plan: RepairPlan, change: ChangeEvent, owner_subject: str) -> None:
        snapshot_hash = plan.snapshot_hash()
        item = {
            **self._proposal_key(plan.id, snapshot_hash),
            "entity_type": {"S": "proposal"},
            "payload": {"S": _proposal_json(plan, change, owner_subject)},
        }
        self.client.put_item(TableName=self.table_name, Item=item)

    def get_proposal(self, plan_id: str, snapshot_hash: str) -> PersistedProposal | None:
        out = self.client.get_item(
            TableName=self.table_name,
            Key=self._proposal_key(plan_id, snapshot_hash),
            ConsistentRead=True,
        )
        item = out.get("Item")
        if not item:
            return None
        return _proposal_from(json.loads(item["payload"]["S"]), snapshot_hash)

    def save_approval(self, plan_id: str, approval: Approval) -> None:
        item = {
            **self._approval_key(plan_id, approval.plan_snapshot_hash),
            "entity_type": {"S": "approval"},
            "payload": {"S": json.dumps(asdict(approval), sort_keys=True, separators=(",", ":"))},
        }
        self.client.put_item(TableName=self.table_name, Item=item)

    def get_approval(self, plan_id: str, snapshot_hash: str) -> Approval | None:
        out = self.client.get_item(
            TableName=self.table_name,
            Key=self._approval_key(plan_id, snapshot_hash),
            ConsistentRead=True,
        )
        item = out.get("Item")
        if not item:
            return None
        return _approval_from(json.loads(item["payload"]["S"]))

    def save_receipt(self, plan_id: str, receipt: ExecutionReceipt) -> None:
        item = {
            **self._receipt_key(receipt.idempotency_key),
            "entity_type": {"S": "receipt"},
            "plan_id": {"S": plan_id},
            "receipt_status": {"S": receipt.status},
            "payload": {"S": json.dumps(asdict(receipt), sort_keys=True, separators=(",", ":"), default=str)},
        }
        try:
            self.client.put_item(
                TableName=self.table_name,
                Item=item,
                ConditionExpression="attribute_not_exists(pk) OR #receipt_status <> :executed",
                ExpressionAttributeNames={"#receipt_status": "receipt_status"},
                ExpressionAttributeValues={":executed": {"S": "executed"}},
            )
        except Exception as exc:
            if self._is_conditional_failure(exc):
                # Another worker (or a prior attempt) already published the
                # authoritative executed receipt. Preserve it exactly.
                return
            raise

    def get_receipt(self, idempotency_key: str) -> ExecutionReceipt | None:
        out = self.client.get_item(
            TableName=self.table_name,
            Key=self._receipt_key(idempotency_key),
            ConsistentRead=True,
        )
        item = out.get("Item")
        if not item:
            return None
        return _receipt_from(json.loads(item["payload"]["S"]))


def build_state_store() -> StateStore:
    backend = os.getenv("RIPPLE_STATE_BACKEND", "memory").strip().lower()
    if backend == "memory":
        return MemoryStateStore()
    if backend == "sqlite":
        return SqliteStateStore(os.getenv("RIPPLE_SQLITE_PATH", "/tmp/ripple-state.sqlite3"))
    if backend == "dynamodb":
        table = os.getenv("RIPPLE_DYNAMODB_TABLE", "").strip()
        if not table:
            raise RuntimeError("RIPPLE_DYNAMODB_TABLE is required for DynamoDB state")
        return DynamoDbStateStore(table, region_name=os.getenv("AWS_REGION") or None)
    raise RuntimeError(f"Unsupported RIPPLE_STATE_BACKEND: {backend}")
