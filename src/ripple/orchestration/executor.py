from __future__ import annotations
from typing import List
from ripple.domain.models import RepairPlan, Approval, ExecutionReceipt, ActionStatus
from ripple.policy.approval import ApprovalPolicy
from ripple.tools.simulated import ToolRegistry


class SimulatedInterruption(RuntimeError):
    pass


class Executor:
    def __init__(self, tools: ToolRegistry):
        self.tools = tools
        self.receipt_log: List[ExecutionReceipt] = []

    def execute(self, plan: RepairPlan, approval: Approval, *, interrupt_after: int | None = None) -> List[ExecutionReceipt]:
        ApprovalPolicy.validate(plan, approval)
        for action in plan.actions:
            self.tools.preflight(action)

        receipts = []
        for processed, action in enumerate(plan.actions, start=1):
            receipt = self.tools.execute(action)
            self.receipt_log.append(receipt)
            if receipt.status == "executed":
                action.status = ActionStatus.EXECUTED
            elif receipt.status == "failed":
                action.status = ActionStatus.FAILED
            else:
                action.status = ActionStatus.SKIPPED
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
