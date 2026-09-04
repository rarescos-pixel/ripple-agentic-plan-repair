from __future__ import annotations
from dataclasses import dataclass
from typing import List
from ripple.domain.models import Approval, ExecutionReceipt
from ripple.orchestration.agent import RippleAgent, AgentResponse
from ripple.orchestration.executor import Executor


@dataclass
class SessionResult:
    proposal: AgentResponse
    receipts: List[ExecutionReceipt]


class RippleSession:
    """Two-phase UX contract: propose first, execute only after exact approval."""
    def __init__(self, agent: RippleAgent, executor: Executor):
        self.agent = agent
        self.executor = executor

    def propose(self, utterance, context) -> AgentResponse:
        return self.agent.propose(utterance, context)

    def execute_with_approval(self, proposal: AgentResponse, approval: Approval) -> SessionResult:
        """Execute only the approval object supplied by the client/UI.

        Crucially, this method never reconstructs approval from the current plan.
        The executor's ApprovalPolicy therefore compares the client-visible snapshot
        hash/version/cost/scope against the current authoritative plan.
        """
        receipts = self.executor.execute(proposal.plan, approval)
        return SessionResult(proposal, receipts)

    def approve_and_execute(self, proposal: AgentResponse, *, max_total_cost: float, external_people_notified: int) -> SessionResult:
        """Compatibility helper for non-UI tests that approve the current snapshot inline."""
        approval = Approval(
            proposal.plan.id,
            proposal.plan.version,
            max_total_cost=max_total_cost,
            external_people_notified=external_people_notified,
            plan_snapshot_hash=proposal.plan.snapshot_hash(),
        )
        return self.execute_with_approval(proposal, approval)
