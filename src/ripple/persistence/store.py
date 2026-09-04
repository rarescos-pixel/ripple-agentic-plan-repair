from __future__ import annotations

from dataclasses import asdict
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Protocol

from ripple.domain.models import Approval, ExecutionReceipt


class StateStore(Protocol):
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


class MemoryStateStore:
    def __init__(self) -> None:
        self.approvals: dict[tuple[str, str], Approval] = {}
        self.receipts: dict[str, ExecutionReceipt] = {}

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
    """Single-table approval/idempotency store.

    boto3 is imported lazily so local development and CI need no AWS SDK unless
    the DynamoDB backend is explicitly selected. A client can be injected for
    deterministic tests.
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
        current = self.get_receipt(receipt.idempotency_key)
        if current is not None and current.status == "executed":
            return
        item = {
            **self._receipt_key(receipt.idempotency_key),
            "entity_type": {"S": "receipt"},
            "plan_id": {"S": plan_id},
            "payload": {"S": json.dumps(asdict(receipt), sort_keys=True, separators=(",", ":"), default=str)},
        }
        self.client.put_item(TableName=self.table_name, Item=item)

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
