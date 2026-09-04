from __future__ import annotations
from dataclasses import dataclass
from typing import List
from ripple.domain.models import RepairPlan, ExecutionReceipt


@dataclass(frozen=True)
class RubricEvidence:
    technical_implementation: List[str]
    design: List[str]
    potential_impact: List[str]
    quality_of_idea: List[str]


def collect_evidence(plan: RepairPlan, receipts: List[ExecutionReceipt]) -> RubricEvidence:
    executed = sum(r.status == "executed" for r in receipts)
    failed = sum(r.status == "failed" for r in receipts)
    deduplicated = sum(r.status == "deduplicated" for r in receipts)
    return RubricEvidence(
        technical_implementation=[
            f"Dependency graph produced {len(plan.impacts)} downstream impacts.",
            f"Bounded saga produced {len(receipts)} authoritative receipts.",
            f"Execution outcome: {executed} executed, {failed} failed, {deduplicated} deduplicated.",
            "All external writes are gated by exact-plan approval and idempotency keys.",
        ],
        design=[
            "One changed fact becomes one compact repair proposal instead of multiple app workflows.",
            f"Approval disclosure includes ${plan.total_added_cost:.0f} added cost and {plan.external_people_notified} external notifications.",
            "The user can approve the exact plan with one confirmation; material drift requires re-approval.",
        ],
        potential_impact=[
            f"Golden scenario avoids up to ${plan.total_avoidable_loss:.0f} in direct loss.",
            f"Golden scenario preserves ${plan.net_direct_cash_preserved:.0f} net direct cash after recovery cost.",
            f"Five downstream commitments are repaired from one spoken change.",
        ],
        quality_of_idea=[
            "Core abstraction is consequence-aware cascading repair, not single-app rescheduling.",
            "The agent reasons over dependencies across heterogeneous commitments and repairs only affected nodes.",
            "Voice interaction is optimized for moments when plans change and attention is scarce.",
        ],
    )
