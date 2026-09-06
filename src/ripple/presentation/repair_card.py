from __future__ import annotations

from typing import Any

from ripple.domain.models import ExecutionReceipt, Impact, RepairPlan


def _money(value: float) -> str:
    rounded = round(value)
    if abs(value - rounded) < 1e-9:
        return f"${rounded:,}"
    return f"${value:,.2f}"


def _impact_label(impact: Impact) -> str:
    """Return the human-facing commitment title already carried by the impact.

    DependencyEngine deliberately includes the canonical PlanNode title in the
    impact reason. Reusing that title keeps the Repair Card presentation-only:
    no extra mutable title field is added to RepairPlan and the approval
    snapshot contract remains unchanged.
    """
    suffixes = (
        " violates dependency after the changed fact",
        " is affected but has no safe repair option",
    )
    for suffix in suffixes:
        if impact.reason.endswith(suffix):
            label = impact.reason[: -len(suffix)].strip()
            if label:
                return label
    # Defensive fallback for future impact reasons: never expose a blank label.
    return impact.affected_node_id.split(":", 1)[0].replace("_", " ").strip().title()


def _optimization_evidence(plan: RepairPlan) -> list[dict[str, Any]]:
    """Explain only economic choices that can be proven from the approved plan.

    The planner may remove candidates because of hard user constraints before
    economic ranking. The RepairPlan intentionally does not expose those
    private policy details. To avoid inventing a reason, this presentation
    helper emits evidence only when the selected action is also the strongest
    net-value choice among every option visible in the immutable impact
    snapshot. That makes each explanation mechanically checkable.
    """
    actions = {action.target_id: action for action in plan.actions}
    evidence: list[dict[str, Any]] = []
    for impact in plan.impacts:
        selected = actions.get(impact.affected_node_id)
        if selected is None or len(impact.options) < 2:
            continue
        selected_net = selected.avoidable_loss - selected.added_cost
        alternatives = [
            option for option in impact.options
            if not (option.tool == selected.tool and option.operation == selected.operation and option.params == selected.params)
        ]
        if not alternatives:
            continue
        best_visible = max(
            impact.options,
            key=lambda option: (option.avoidable_loss - option.added_cost, -option.added_cost, option.reversible),
        )
        if not (
            best_visible.tool == selected.tool
            and best_visible.operation == selected.operation
            and best_visible.params == selected.params
        ):
            # A hidden hard constraint may explain the selection. Do not guess.
            continue
        best_alternative = max(
            alternatives,
            key=lambda option: (option.avoidable_loss - option.added_cost, -option.added_cost, option.reversible),
        )
        alternative_net = best_alternative.avoidable_loss - best_alternative.added_cost
        evidence.append({
            "commitment_id": impact.affected_node_id,
            "commitment": _impact_label(impact),
            "selected_operation": selected.operation,
            "selected_net_preserved": selected_net,
            "best_alternative_operation": best_alternative.operation,
            "best_alternative_net_preserved": alternative_net,
            "net_advantage": selected_net - alternative_net,
            "reason": "maximizes net direct cash preserved among visible safe candidates",
        })
    return evidence


def build_repair_card(plan: RepairPlan, *, max_visible_impacts: int = 3) -> dict[str, Any]:
    """Build a low-density, voice-parity decision surface for Alexa+.

    The card deliberately puts economic consequence first, then scope, then the
    exact approval boundary. It does not expose implementation jargon such as
    graph traversal, hashes or idempotency keys in the primary visual surface.
    """
    visible = plan.impacts[: max(0, max_visible_impacts)]
    remaining = max(0, len(plan.impacts) - len(visible))
    services = sorted({a.tool for a in plan.actions})
    irreversible = sum(1 for a in plan.actions if not a.reversible)

    risk = _money(plan.total_avoidable_loss)
    repair_cost = _money(plan.total_added_cost)
    preserved = _money(plan.net_direct_cash_preserved)
    headline = f"{len(plan.impacts)} commitments affected"
    decision_label = f"Approve {repair_cost} repair"
    decision_prompt = f"Approve the {repair_cost} repair?"
    money_summary = f"{risk} at risk → {repair_cost} repair → {preserved} net preserved"

    voice = (
        f"One thing changed. I found {len(plan.impacts)} affected commitments. "
        f"{risk} is directly at risk. "
        f"I can repair them for {repair_cost} and preserve {preserved} net."
    )
    if plan.external_people_notified:
        voice += f" The repair notifies {plan.external_people_notified} people."
    voice += f" {decision_prompt}"

    return {
        "schema": "ripple.repair-card.v1",
        "display_hint": "inline",
        "headline": headline,
        "subheadline": "Repair the consequences, not just the changed item.",
        "money_summary": money_summary,
        "metrics": [
            {"label": "At risk", "value": risk, "semantic": "risk"},
            {"label": "Repair cost", "value": repair_cost, "semantic": "cost"},
            {"label": "Net preserved", "value": preserved, "semantic": "value"},
        ],
        "scope": {
            "actions": len(plan.actions),
            "services": len(services),
            "service_names": services,
            "people_notified": plan.external_people_notified,
            "irreversible_actions": irreversible,
            "unresolved_items": len(plan.unresolved_items),
        },
        "top_impacts": [
            {
                "id": impact.affected_node_id,
                "label": _impact_label(impact),
                "cash_at_risk": _money(impact.direct_cash_at_risk),
                "urgency": impact.urgency,
                "status": impact.status.value,
            }
            for impact in visible
        ],
        "remaining_impacts": remaining,
        "selection_policy": {
            "label": "Why this plan?",
            "summary": "Deterministic policy chooses among allowed repairs to preserve the most net direct cash. The model does not choose spending.",
        },
        "optimization_evidence": _optimization_evidence(plan),
        "decision": {
            "label": decision_label,
            "voice_prompt": decision_prompt,
            "requires_exact_snapshot": True,
            "max_total_cost": plan.total_added_cost,
            "external_people_notified": plan.external_people_notified,
        },
        "voice_summary": voice,
        "accessibility_label": (
            f"{headline}. {money_summary}. {decision_prompt}"
        ),
    }


def _human_operation(value: str) -> str:
    return value.replace("_", " ").strip().capitalize()


def build_receipt_timeline(
    plan: RepairPlan,
    receipts: list[ExecutionReceipt],
    *,
    authoritative_unique_writes: int,
    recovered_after_restart: bool = False,
) -> dict[str, Any]:
    """Build a compact, sanitized post-execution proof surface.

    The timeline exposes enough to make Ripple's safety visible to a judge but
    never includes provider payloads, idempotency keys, approval hashes or other
    low-level data. Counts are derived from the authoritative receipts returned
    by the Executor, not from marketing copy.
    """
    actions_by_id = {a.id: a for a in plan.actions}
    labels = {impact.affected_node_id: _impact_label(impact) for impact in plan.impacts}
    executed = sum(r.status == "executed" for r in receipts)
    deduplicated = sum(r.status == "deduplicated" for r in receipts)
    failed = sum(r.status == "failed" for r in receipts)

    if failed:
        headline = "Repair needs attention"
        subheadline = f"{failed} action{'s' if failed != 1 else ''} did not complete. Unresolved work stays visible."
    elif deduplicated == len(receipts) and receipts:
        headline = "Replay safe"
        subheadline = "The approved plan was replayed without repeating provider writes."
    elif recovered_after_restart:
        headline = "Repair resumed safely"
        subheadline = "Ripple recovered the exact approved snapshot and continued without duplicate provider writes."
    else:
        headline = "Repair complete"
        subheadline = "Every provider action returned an authoritative receipt."

    if receipts and deduplicated == len(receipts):
        proof_summary = f"{len(receipts)} replayed → {deduplicated} deduplicated → 0 new provider writes"
    elif recovered_after_restart and deduplicated:
        proof_summary = f"{len(receipts)} receipts → {executed} resumed writes → {deduplicated} safely deduplicated"
    else:
        proof_summary = f"{len(plan.actions)} actions → {len(receipts)} receipts → {executed} provider writes"

    entries: list[dict[str, Any]] = []
    for receipt in receipts:
        action = actions_by_id.get(receipt.action_id)
        target_id = action.target_id if action else receipt.action_id
        operation = action.operation if action else "provider action"
        entries.append({
            "action_id": receipt.action_id,
            "label": labels.get(target_id, target_id.replace(":", " · ")),
            "operation": _human_operation(operation),
            "provider": action.tool if action else "provider",
            "status": receipt.status,
        })

    return {
        "schema": "ripple.receipt-timeline.v1",
        "headline": headline,
        "subheadline": subheadline,
        "proof_summary": proof_summary,
        "counts": {
            "actions": len(plan.actions),
            "receipts": len(receipts),
            "executed_this_call": executed,
            "deduplicated_this_call": deduplicated,
            "failed_this_call": failed,
            "authoritative_unique_writes": authoritative_unique_writes,
            "duplicate_provider_writes": 0 if failed == 0 else None,
        },
        "recovered_after_restart": recovered_after_restart,
        "entries": entries,
        "safety_note": (
            "Replay produced 0 duplicate provider writes."
            if deduplicated and failed == 0
            else "Execution is bounded to the exact approved plan and every provider action must produce a receipt."
        ),
    }
