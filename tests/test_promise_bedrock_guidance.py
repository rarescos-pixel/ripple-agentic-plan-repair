"""Regression guard for the generic live-Bedrock intent generation guidance."""

from ripple.promises.interpreter import RULES


def test_temporal_guidance_is_generic_postfix_not_hero_logic():
    assert "POSTFIX/RPN EXPRESSION FORMAT" in RULES
    assert "Never JSON-encode the whole contract into a string" in RULES
    assert "Do not emit IDs, roots, references, args, nested expressions or unused tokens" in RULES
    assert "$now alone is never a logical operand" in RULES
    assert "fact $now, fact TIME, operator lt, fact CONTROL, literal string CURRENT, operator eq, operator implies" in RULES
    assert "goal_time is one fact atom for TIME" in RULES
    assert "Snapshot assumption TIME == CURRENT_TIME" in RULES
    assert "Omit expiry_when unless the human separately supplied an independent boolean expiry condition" in RULES
    for hero_term in ("Mom", "mom_left", "flight_changed", "occupant_access", "departure_at"):
        assert hero_term not in RULES


def test_outcome_and_lifetime_completion_are_explicitly_separate_roles():
    assert "ROLE SEPARATION IS MANDATORY" in RULES
    assert "desired_outcome = the world state/result" in RULES
    assert "lifetime_completion = the separate condition" in RULES
    assert "goal_time = when desired_outcome is due" in RULES
    assert "Never put lifetime_completion in desired_outcome" in RULES
    assert "Never omit lifetime_completion because desired_outcome exists" in RULES


def test_authority_guidance_preserves_explicit_human_prohibitions():
    assert "never change a supplied fact/control" in RULES
    assert "set that exact name to FORBIDDEN" in RULES
    assert "OBSERVE does not satisfy an explicit no-change prohibition" in RULES
    assert "set it to APPROVAL_REQUIRED unless the same name is explicitly FORBIDDEN" in RULES
    assert "never action approval and never meaning confirmation" in RULES
