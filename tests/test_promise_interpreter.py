"""Regressions at the untrusted model boundary, including the captured live failure."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from test_promise_acceptance import setup_engine
from test_promise_interface import DraftModel
from ripple.promises.interpreter import BedrockIntentInterpreter, decode_contract
from ripple.promises.model import validate_contract


def context(engine, provider, clock):
    return {"world": provider.read()["facts"], "catalog": engine.catalog,
            "now": clock(), "source": "test-world"}


@pytest.mark.parametrize("domain", ["business", "software", "household"])
def test_model_receives_canonical_typed_schema_and_real_authority_names(tmp_path, domain):
    engine, provider, clock, state = setup_engine(tmp_path, domain)
    model = DraftModel(state["contract"])
    draft = BedrockIntentInterpreter(model, "test").interpret("Keep the specified promise", context(engine, provider, clock))
    assert draft == state["contract"]  # no post-hoc contract replacement or coercion
    schema = model.request["toolConfig"]["tools"][0]["toolSpec"]["inputSchema"]["json"]
    assert set(schema["properties"]) == {"contract_json", "confidence"}
    assert schema["properties"]["contract_json"]["type"] == "string"
    contract = json.loads(model.request["system"][0]["text"].split("\nCONTRACT_SCHEMA=")[1])
    assert set(contract["required"]) == set(draft)
    fields = contract["properties"]
    assert fields["goal_at"]["properties"]["literal"]["type"] == "integer"
    assert "operator" not in fields["goal"]["properties"]
    assert {"eq", "implies", "not", "fact", "literal"} <= set(fields["goal"]["properties"])
    assert fields["authority"]["additionalProperties"] is False
    assert set(fields["authority"]["properties"]) == set(provider.read()["facts"])
    for name, permission in fields["authority"]["properties"].items():
        assert "AUTONOMOUS_REVERSIBLE" not in permission["enum"]
        assert ("APPROVAL_REQUIRED" in permission["enum"]) == (name in engine.catalog)
    assert fields["evidence"]["properties"]["source"]["enum"] == ["test-world"]
    assert provider.write_count() == 0


def test_captured_live_bedrock_failure_is_still_rejected():
    evidence = json.loads((Path(__file__).parents[1] / "docs/PROMISE_AWS_LIVE_EVIDENCE.json").read_text())
    class Captured:
        def converse(self, **kwargs): return deepcopy(evidence["bedrock_response"])
    request = evidence["bedrock_request"]
    with pytest.raises(ValueError):
        BedrockIntentInterpreter(Captured(), "test").interpret(request["utterance"], request["context"])
    # Encoding that same malformed AST in the new transport cannot rescue it.
    invalid = evidence["bedrock_response"]["output"]["message"]["content"][0]["toolUse"]["input"]["contract"]
    with pytest.raises(ValueError, match="Unsupported deterministic operator"):
        BedrockIntentInterpreter(DraftModel(invalid), "test").interpret(request["utterance"], request["context"])


@pytest.mark.parametrize("field,value", [
    ("goal_at", {"eq": [{"fact": "deadline"}, {"literal": 100}]}),
    ("goal_at", {"literal": True}),
    ("goal_at", {"literal": 100.0}),
    ("goal", {"fact": "delivery_route"}),
    ("completion", {"fact": "deadline"}),
    ("goal", {"and": [{"literal": False}, {"fact": "deadline"}]}),
    ("goal", {"eq": [{"fact": "deadline"}, {"literal": "100"}]}),
    ("goal", {"lt": [{"fact": "finished"}, {"literal": True}]}),
])
def test_structurally_valid_but_ill_typed_model_predicates_are_rejected(tmp_path, field, value):
    engine, provider, clock, state = setup_engine(tmp_path)
    spec = deepcopy(state["contract"])
    spec[field] = value
    validate_contract(spec)  # structural validity alone does not imply typed meaning
    with pytest.raises(ValueError, match="type|boolean|integer"):
        BedrockIntentInterpreter(DraftModel(spec), "test").interpret("x", context(engine, provider, clock))
    assert provider.write_count() == 0


@pytest.mark.parametrize("collection", ["invariants", "assumptions"])
def test_predicate_collections_require_boolean_meaning(tmp_path, collection):
    engine, provider, clock, state = setup_engine(tmp_path)
    spec = deepcopy(state["contract"])
    spec[collection][0]["predicate"] = {"fact": "deadline"}
    with pytest.raises(ValueError, match="boolean"):
        BedrockIntentInterpreter(DraftModel(spec), "test").interpret("x", context(engine, provider, clock))


@pytest.mark.parametrize("stop", ["max_tokens", "guardrail_intervened", "end_turn", "malformed_tool_use", None])
def test_incomplete_or_non_tool_response_cannot_become_a_contract(tmp_path, stop):
    engine, provider, clock, state = setup_engine(tmp_path)
    class Interrupted(DraftModel):
        def converse(self, **kwargs):
            response = super().converse(**kwargs)
            response["stopReason"] = stop
            return response
    with pytest.raises(ValueError, match="tool-use"):
        BedrockIntentInterpreter(Interrupted(state["contract"]), "test").interpret("x", context(engine, provider, clock))


@pytest.mark.parametrize("change", [
    lambda s: s["authority"].update(delivery_route="AUTONOMOUS_REVERSIBLE"),
    lambda s: s["authority"].update(budget_ok="APPROVAL_REQUIRED"),
    lambda s: s["evidence"].update(source="invented"),
    lambda s: s["expiry"].update(when={"fact": "deadline"}),
    lambda s: s["invariants"][0].update(predicate={"operator": ["eq", True, True]}),
])
def test_invalid_authority_evidence_and_predicates_stay_fail_closed(tmp_path, change):
    engine, provider, clock, state = setup_engine(tmp_path)
    spec = deepcopy(state["contract"])
    change(spec)
    with pytest.raises(ValueError):
        BedrockIntentInterpreter(DraftModel(spec), "test").interpret("x", context(engine, provider, clock))
    assert provider.write_count() == 0


@pytest.mark.parametrize("encoded", [
    '{"goal":true,"goal":false}',
    '{"nested":{"x":1,"x":2}}',
    '{"literal":NaN}', '{"literal":Infinity}',
    '```json\n{}\n```', '{} trailing', '', {},
])
def test_json_transport_does_not_repair_malformed_or_ambiguous_data(encoded):
    with pytest.raises(ValueError): decode_contract(encoded)
