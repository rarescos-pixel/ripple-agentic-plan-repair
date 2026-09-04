from __future__ import annotations
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import json


class NodeKind(str, Enum):
    FACT = "fact"
    CALENDAR = "calendar"
    RIDE = "ride"
    RESERVATION = "reservation"
    DELIVERY = "delivery"
    CARE = "care"


class NodeStatus(str, Enum):
    PLANNED = "planned"
    CHANGED = "changed"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"
    PENDING = "pending"


class ImpactStatus(str, Enum):
    SAFE = "safe"
    AT_RISK = "at_risk"
    INVALID = "invalid"


class ActionStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    EXECUTED = "executed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class PlanNode:
    id: str
    kind: NodeKind
    title: str
    status: NodeStatus = NodeStatus.PLANNED
    start_at: Optional[str] = None
    end_at: Optional[str] = None
    financial_exposure: float = 0.0
    external_people: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)
    version: int = 1

    def evolved(self, **changes: Any) -> "PlanNode":
        return replace(self, version=self.version + 1, **changes)


@dataclass(frozen=True)
class DependencyEdge:
    upstream_id: str
    downstream_id: str
    relation: str
    severity: str = "high"
    condition: str = "always"


@dataclass(frozen=True)
class ChangeEvent:
    id: str
    node_id: str
    field: str
    old_value: Any
    new_value: Any
    source: str = "voice"
    confidence: float = 1.0
    correlation_id: str = "golden"


@dataclass(frozen=True)
class RepairOption:
    tool: str
    operation: str
    params: Dict[str, Any]
    added_cost: float = 0.0
    avoidable_loss: float = 0.0
    reversible: bool = True
    external_side_effect: bool = True


@dataclass(frozen=True)
class Impact:
    affected_node_id: str
    dependency_path: List[str]
    reason: str
    status: ImpactStatus
    direct_cash_at_risk: float
    urgency: int
    options: List[RepairOption]


@dataclass
class RepairAction:
    id: str
    tool: str
    operation: str
    target_id: str
    params: Dict[str, Any]
    reversible: bool
    external_side_effect: bool
    added_cost: float
    avoidable_loss: float
    idempotency_key: str
    approval_level: str = "explicit_plan"
    status: ActionStatus = ActionStatus.PROPOSED


@dataclass
class RepairPlan:
    id: str
    version: int
    source_change_event_id: str
    impacts: List[Impact]
    actions: List[RepairAction]
    total_added_cost: float
    total_avoidable_loss: float
    external_people_notified: int
    unresolved_items: List[str] = field(default_factory=list)
    status: str = "proposed"

    @property
    def net_direct_cash_preserved(self) -> float:
        return self.total_avoidable_loss - self.total_added_cost

    def snapshot_hash(self) -> str:
        """Content hash for the exact approval snapshot.

        Version numbers are useful but insufficient: a mutable in-memory plan
        could drift without a version bump. Approval binds to this canonical
        content hash as well as id/version.
        """
        payload = {
            "id": self.id,
            "version": self.version,
            "source_change_event_id": self.source_change_event_id,
            "impacts": [
                {
                    "affected_node_id": i.affected_node_id,
                    "dependency_path": list(i.dependency_path),
                    "reason": i.reason,
                    "status": i.status.value,
                    "direct_cash_at_risk": i.direct_cash_at_risk,
                    "urgency": i.urgency,
                    "options": [
                        {
                            "tool": o.tool,
                            "operation": o.operation,
                            "params": o.params,
                            "added_cost": o.added_cost,
                            "avoidable_loss": o.avoidable_loss,
                            "reversible": o.reversible,
                            "external_side_effect": o.external_side_effect,
                        }
                        for o in i.options
                    ],
                }
                for i in self.impacts
            ],
            "actions": [
                {
                    "id": a.id,
                    "tool": a.tool,
                    "operation": a.operation,
                    "target_id": a.target_id,
                    "params": a.params,
                    "reversible": a.reversible,
                    "external_side_effect": a.external_side_effect,
                    "added_cost": a.added_cost,
                    "avoidable_loss": a.avoidable_loss,
                    "idempotency_key": a.idempotency_key,
                }
                for a in self.actions
            ],
            "total_added_cost": self.total_added_cost,
            "total_avoidable_loss": self.total_avoidable_loss,
            "external_people_notified": self.external_people_notified,
            "unresolved_items": list(self.unresolved_items),
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(raw.encode()).hexdigest()


@dataclass(frozen=True)
class Approval:
    plan_id: str
    plan_version: int
    max_total_cost: float
    external_people_notified: int
    plan_snapshot_hash: str
    actor: str = "user"


@dataclass(frozen=True)
class ExecutionReceipt:
    action_id: str
    idempotency_key: str
    status: str
    result: Dict[str, Any]
    attempt: int = 1
