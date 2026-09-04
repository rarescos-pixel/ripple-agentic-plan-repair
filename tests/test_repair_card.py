from ripple.golden import build_golden
from ripple.presentation import build_repair_card


def test_golden_repair_card_is_low_density_and_money_first():
    _, _, planner, _, change = build_golden()
    plan = planner.build_plan(change)
    card = build_repair_card(plan)

    assert card["schema"] == "ripple.repair-card.v1"
    assert card["display_hint"] == "inline"
    assert card["headline"] == "5 commitments affected"
    assert [m["value"] for m in card["metrics"]] == ["$116", "$42", "$74"]
    assert card["decision"]["label"] == "Approve $42 repair"
    assert card["decision"]["requires_exact_snapshot"] is True
    assert len(card["top_impacts"]) == 3
    assert card["remaining_impacts"] == 2
    assert "5 affected commitments" in card["voice_summary"]
    assert "$116" in card["voice_summary"]
    assert "$74" in card["voice_summary"]
