"""Regression guard for the generic live-Bedrock intent generation guidance."""

from ripple.promises.interpreter import RULES


def test_temporal_guidance_is_generic_flat_ast_not_hero_logic():
    assert "FLAT AST WIRE FORMAT" in RULES
    assert "Never JSON-encode the whole contract into a string" in RULES
    assert "operator and args containing only node ids" in RULES
    assert "Do not nest expression objects inside args" in RULES
    assert "$now fact node alone is never a logical operand" in RULES
    assert "lt($now,TIME), eq(CONTROL,CURRENT), then implies(lt-root,eq-root)" in RULES
    assert "TIME, CONTROL and CURRENT above are metasyntax only" in RULES
    for hero_term in ("Mom", "mom_left", "flight_changed", "occupant_access", "departure_at"):
        assert hero_term not in RULES


def test_authority_guidance_preserves_explicit_human_prohibitions():
    assert "never change a supplied fact/control" in RULES
    assert "set that exact name to FORBIDDEN" in RULES
    assert "OBSERVE does not satisfy an explicit no-change prohibition" in RULES
    assert "set it to APPROVAL_REQUIRED unless the same name is explicitly FORBIDDEN" in RULES
    assert "never action approval and never meaning confirmation" in RULES
