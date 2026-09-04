from ripple.domain.models import RepairPlan, Approval


class ApprovalPolicy:
    @staticmethod
    def requires_approval(plan: RepairPlan) -> bool:
        return any(a.external_side_effect for a in plan.actions)

    @staticmethod
    def validate(plan: RepairPlan, approval: Approval) -> None:
        if approval.plan_id != plan.id or approval.plan_version != plan.version:
            raise ValueError("Approval does not match exact plan snapshot")
        if approval.plan_snapshot_hash != plan.snapshot_hash():
            raise ValueError("Plan content drifted after approval; re-approval required")
        if plan.total_added_cost > approval.max_total_cost:
            raise ValueError("Plan cost exceeds approved maximum")
        if plan.external_people_notified > approval.external_people_notified:
            raise ValueError("Plan adds external notifications beyond approved scope")
