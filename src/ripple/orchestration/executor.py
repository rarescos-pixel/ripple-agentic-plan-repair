from __future__ import annotations
from typing import List

from ripple.domain.models import RepairPlan, Approval, ExecutionReceipt, ActionStatus
from ripple.persistence import StateStore, build_state_store
from ripple.policy.approval import ApprovalPolicy
from ripple.tools.simulated import ToolRegistry


class SimulatedInterruption(RuntimeError):
    pass


class Executor:
    def __init__(self, tools: ToolRegistry, store: StateStore | None = None):
        self.tools = tools
        self.store = store or build_state_store()
        self.receipt_log: List[ExecutionReceipt] = []

    def record_approval(self, plan: RepairPlan, approval: Approval) -> Approval:
        """Validate and durably record the exact approval snapshot before writes."""
        ApprovalPolicy.validate(plan, approval)
        self.store.save_approval(plan.id, approval)
        return approval

    def load_approval(self, plan: RepairPlan) -> Approval | None:
        """Load a previously persisted approval for the plan's current snapshot."""
        return self.store.get_approval(plan.id, plan.snapshot_hash())

    def execute(self, plan: RepairPlan, approval: Approval, *, interrupt_after: int | None = None) -> List[ExecutionReceipt]:
        self.record_approval(plan, approval)
        for action in plan.actions:
            self.tools.preflight(action)

        receipts: List[ExecutionReceipt] = []
        for processed, action in enumerate(plan.actions, start=1):
            committed = self.store.get_receipt(action.idempotency_key)
            if committed is not None and committed.status == "executed":
                receipt = ExecutionReceipt(
                    action_id=action.id,
                    idempotency_key=action.idempotency_key,
                    status="deduplicated",
                    result=dict(committed.result),
                    attempt=committed.attempt + 1,
                )
                action.status = ActionStatus.SKIPPED
            else:
                receipt = self.tools.execute(action)
                self.store.save_receipt(plan.id, receipt)
                if receipt.status == "executed":
                    action.status = ActionStatus.EXECUTED
                elif receipt.status == "failed":
                    action.status = ActionStatus.FAILED
                else:
                    action.status = ActionStatus.SKIPPED

            self.receipt_log.append(receipt)
            receipts.append(receipt)
            if interrupt_after is not None and processed >= interrupt_after:
                plan.status = "interrupted"
                raise SimulatedInterruption(f"Simulated interruption after {processed} actions")

        if any(r.status == "failed" for r in receipts):
            plan.status = "partial"
        elif plan.unresolved_items:
            plan.status = "partial"
        else:
            plan.status = "executed"
        return receipts
