from ripple.golden import build_golden
from ripple.presentation import build_repair_card


def test_golden_repair_card_is_low_density_money_first_and_human_readable():
    _, _, planner, _, change = build_golden()
    plan = planner.build_plan(change)
    card = build_repair_card(plan)

    assert card["schema"] == "ripple.repair-card.v1"
    assert card["display_hint"] == "inline"
    assert card["headline"] == "5 commitments affected"
    assert card["money_summary"] == "$116 at risk → $42 repair → $74 net preserved"
    assert [m["value"] for m in card["metrics"]] == ["$116", "$42", "$74"]
    assert card["decision"]["label"] == "Approve $42 repair"
    assert card["decision"]["voice_prompt"] == "Approve the $42 repair?"
    assert card["decision"]["requires_exact_snapshot"] is True
    assert len(card["top_impacts"]) == 3
    assert [impact["label"] for impact in card["top_impacts"]] == [
        "Dinner reservation",
        "Pet care",
        "Airport pickup",
    ]
    assert card["remaining_impacts"] == 2
    assert card["voice_summary"].startswith("One thing changed. I found 5 affected commitments.")
    assert "$116 is directly at risk" in card["voice_summary"]
    assert "repair them for $42 and preserve $74 net" in card["voice_summary"]
    assert card["voice_summary"].endswith("Approve the $42 repair?")
    assert card["accessibility_label"].endswith("Approve the $42 repair?")


def test_repair_card_keeps_density_bound_and_has_safe_label_fallback():
    _, _, planner, _, change = build_golden()
    plan = planner.build_plan(change)
    # Future/nonstandard reason wording must not leak a blank label or increase
    # the visual density contract.
    first = plan.impacts[0]
    object.__setattr__(first, "reason", "nonstandard future reason")
    card = build_repair_card(plan, max_visible_impacts=1)
    assert len(card["top_impacts"]) == 1
    assert card["remaining_impacts"] == 4
    assert card["top_impacts"][0]["label"] == "Reservation"


def test_repair_card_allows_zero_visible_impacts_without_negative_slice_surprise():
    _, _, planner, _, change = build_golden()
    plan = planner.build_plan(change)
    card = build_repair_card(plan, max_visible_impacts=-1)
    assert card["top_impacts"] == []
    assert card["remaining_impacts"] == 5
