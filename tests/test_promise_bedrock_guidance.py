"""Regression guard for the generic live-Bedrock intent generation guidance."""
import json

from ripple.promises.interpreter import RULES


def test_temporal_guidance_is_valid_generic_ast_not_hero_logic():
    temporal = '{"implies":[{"lt":[{"fact":"$now"},{"fact":"TIME"}]},{"eq":[{"fact":"CONTROL"},{"literal":"CURRENT"}]}]}'
    assert json.loads(temporal) == {
        "implies": [
            {"lt": [{"fact": "$now"}, {"fact": "TIME"}]},
            {"eq": [{"fact": "CONTROL"}, {"literal": "CURRENT"}]},
        ]
    }
    assert temporal in RULES
    assert "Every item inside and/or/implies is a separate complete expression object with exactly one key" in RULES
    assert '{"fact":"$now"} alone is NEVER a logical operand' in RULES
    assert "TIME, CONTROL and CURRENT in that example are metasyntax only" in RULES
    for hero_term in ("Mom", "mom_left", "flight_changed", "occupant_access", "departure_at"):
        assert hero_term not in RULES


def test_authority_guidance_preserves_explicit_human_prohibitions():
    assert "never change a supplied fact/control" in RULES
    assert "set that exact authority entry to FORBIDDEN" in RULES
    assert "OBSERVE does not satisfy an explicit no-change prohibition" in RULES
    assert "set that authority entry to APPROVAL_REQUIRED unless the same name is explicitly FORBIDDEN" in RULES
    assert "never action approval and never meaning confirmation" in RULES
