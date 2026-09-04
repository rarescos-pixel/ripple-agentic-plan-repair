from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Set
from ripple.domain.models import PlanNode, RepairOption, ExecutionReceipt


@dataclass
class SimulatedTool:
    name: str
    execution_log: List[str]
    fail_operations: Set[str]

    def execute(self, action_id: str, idempotency_key: str, operation: str, target_id: str, params: Dict[str, Any]) -> ExecutionReceipt:
        if idempotency_key in self.execution_log:
            return ExecutionReceipt(action_id, idempotency_key, "deduplicated", {"target_id": target_id, "operation": operation})
        if operation in self.fail_operations:
            return ExecutionReceipt(action_id, idempotency_key, "failed", {"target_id": target_id, "operation": operation, "error": "simulated_provider_failure"})
        self.execution_log.append(idempotency_key)
        return ExecutionReceipt(action_id, idempotency_key, "executed", {"target_id": target_id, "operation": operation, "params": params})


class ToolRegistry:
    def __init__(self, fail_operations=None, ambiguous_operations=None) -> None:
        shared_log: List[str] = []
        fail_operations = set(fail_operations or [])
        self.ambiguous_operations = set(ambiguous_operations or [])
        self.tools = {
            name: SimulatedTool(name, shared_log, fail_operations)
            for name in ["calendar", "ride", "reservation", "delivery", "care"]
        }
        self.execution_log = shared_log

    def repair_options(self, node: PlanNode) -> List[RepairOption]:
        a = node.attributes
        if node.kind.value == "ride":
            return [RepairOption("ride", "reschedule_ride", {"new_start_at": a["new_start_at"]}, added_cost=a.get("added_cost", 0), avoidable_loss=node.financial_exposure)]
        if node.kind.value == "reservation":
            if a.get("deadline_missed"):
                return []
            options = [RepairOption("reservation", "cancel_reservation", {"deadline_minutes": a.get("deadline_minutes", 0)}, added_cost=0, avoidable_loss=node.financial_exposure, reversible=False)]
            if a.get("new_start_at") is not None:
                options.append(RepairOption(
                    "reservation", "reschedule_reservation",
                    {"new_start_at": a["new_start_at"]},
                    added_cost=float(a.get("reschedule_cost", 0)),
                    avoidable_loss=node.financial_exposure,
                    reversible=True,
                ))
            return options
        if node.kind.value == "delivery":
            return [RepairOption("delivery", "reschedule_delivery", {"new_start_at": a["new_start_at"]}, added_cost=0, avoidable_loss=node.financial_exposure)]
        if node.kind.value == "care":
            return [RepairOption("care", "extend_booking", {"new_end_at": a["new_end_at"]}, added_cost=a["added_cost"], avoidable_loss=0)]
        if node.kind.value == "calendar":
            return [RepairOption("calendar", "reschedule_event", {"new_start_at": a["new_start_at"], "notify_attendees": True}, added_cost=0, avoidable_loss=0)]
        return []

    def preflight(self, action) -> None:
        if action.operation in self.ambiguous_operations:
            raise ValueError(f"Provider state ambiguous for {action.operation}; execution blocked")

    def execute(self, action):
        return self.tools[action.tool].execute(action.id, action.idempotency_key, action.operation, action.target_id, action.params)
