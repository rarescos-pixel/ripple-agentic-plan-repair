from __future__ import annotations

from typing import Any

from ripple.domain.models import Impact, RepairPlan


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