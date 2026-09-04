from __future__ import annotations

from typing import Any

from ripple.domain.models import RepairPlan


def _money(value: float) -> str:
    rounded = round(value)
    if abs(value - rounded) < 1e-9:
        return f"${rounded:,}"
    return f"${value:,.2f}"


def build_repair_card(plan: RepairPlan, *, max_visible_impacts: int = 3) -> dict[str, Any]:
    """Build a low-density, voice-parity decision surface for Alexa+.

    The card deliberately puts economic consequence first, then scope, then the
    exact approval boundary. It does not expose implementation jargon such as
    graph traversal, hashes or idempotency keys in the primary visual surface.
    """
    visible = plan.impacts[:max_visible_impacts]
    remaining = max(0, len(plan.impacts) - len(visible))
    services = sorted({a.tool for a in plan.actions})
    irreversible = sum(1 for a in plan.actions if not a.reversible)

    headline = f"{len(plan.impacts)} commitments affected"
    voice = (
        f"I found {len(plan.impacts)} affected commitments. "
        f"{_money(plan.total_avoidable_loss)} is directly at risk. "
        f"I can repair the cascade for {_money(plan.total_added_cost)} and preserve "
        f"{_money(plan.net_direct_cash_preserved)} net."
    )
    if plan.external_people_notified:
        voice += f" The repair notifies {plan.external_people_notified} people."
    voice += " I need your approval before I change anything."

    return {
        "schema": "ripple.repair-card.v1",
        "display_hint": "inline",
        "headline": headline,
        "subheadline": "Repair the consequences, not just the changed item.",
        "metrics": [
            {"label": "At risk", "value": _money(plan.total_avoidable_loss), "semantic": "risk"},
            {"label": "Repair cost", "value": _money(plan.total_added_cost), "semantic": "cost"},
            {"label": "Net preserved", "value": _money(plan.net_direct_cash_preserved), "semantic": "value"},
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
                "cash_at_risk": _money(impact.direct_cash_at_risk),
                "urgency": impact.urgency,
                "status": impact.status.value,
            }
            for impact in visible
        ],
        "remaining_impacts": remaining,
        "decision": {
            "label": f"Approve {_money(plan.total_added_cost)} repair",
            "requires_exact_snapshot": True,
            "max_total_cost": plan.total_added_cost,
            "external_people_notified": plan.external_people_notified,
        },
        "voice_summary": voice,
        "accessibility_label": (
            f"{headline}. {_money(plan.total_avoidable_loss)} at risk; "
            f"repair costs {_money(plan.total_added_cost)}; "
            f"net preserved {_money(plan.net_direct_cash_preserved)}."
        ),
    }
