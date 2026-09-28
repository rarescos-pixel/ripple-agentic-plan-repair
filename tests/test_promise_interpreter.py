"""Regressions at the untrusted model boundary, including captured live failures."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from test_promise_acceptance import setup_engine
from test_promise_interface import DraftModel, contract_wire
from ripple.promises.interpreter import BedrockIntentInterpreter, normalize_wire
from ripple.promises.model import validate_contract


def context(engine, provider, clock):
    return {"world": provider.read()["facts"], "catalog": engine.catalog,
            "now": clock(), "source": "test-world"}


@pytest.mark.parametrize("domain", ["business", "software", "household"])
def test_model_receives_flat_typed_wire_schema_and_real_authority_names(tmp_path, domain):
    engine, provider, clock, state = setup_engine(tmp_path, domain)
    model = DraftModel(state["contract"])
    draft = BedrockIntentInterpreter(model, "test").interpret("Keep the specified promise", context(engine, provider, clock))
    assert draft == state["contract"]  # representation normalization only; no semantic replacement
    schema = model.request["toolConfig"]["tools"][0]["toolSpec"]["inputSchema"]["json"]
    fields = schema["properties"]
    assert "contract_json" not in fields
    assert {"nodes", "goal_root", "goal_at_root", "invariants", "assumptions", "authority",
            "expiry_at", "evidence_source", "evidence_max_age_seconds", "completion_root",
            "meaning", "questions", "confidence"} <= set(fields)
    node = fields["nodes"]["items"]
    assert node["additionalProperties"] is False
    assert node["properties"]["kind"]["enum"] == ["fact", "literal", "operator"]
    assert set(node["properties"]["fact"]["enum"]) == set(provider.read()["facts"]) | {"$now"}
    assert node["properties"]["args"]["items"]["type"] == "string"  # non-recursive wire transport
    authority = fields["authority"]["items"]
    assert authority["additionalProperties"] is False
    assert set(authority["properties"]["name"]["enum"]) == set(provider.read()["facts"])
    assert "AUTONOMOUS_REVERSIBLE" not in authority["properties"]["permission"]["enum"]
    assert fields["evidence_source"]["enum"] == ["test-world"]
    assert "CONTRACT_SCHEMA=" not in model.request["system"][0]["text"]
    assert provider.write_count() == 0


def test_captured_live_bedrock_failures_are_still_rejected():
    evidence = json.loads((Path(__file__).parents[1] / "docs/PROMISE_AWS_LIVE_EVIDENCE.json").read_text())
    class Captured:
        def converse(self, **kwargs): return deepcopy(evidence["bedrock_response"])
    request = evidence["bedrock_request"]
    with pytest.raises(ValueError):
        BedrockIntentInterpreter(Captured(), "test").interpret(request["utterance"], request["context"])
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


@pytest.mark.parametrize("case", [
    "duplicate_node", "missing_root", "unused_node", "cycle",
    "ambiguous_node", "bad_literal", "duplicate_authority", "legacy_string_transport",
])
def test_flat_wire_rejects_graph_ambiguity_and_malformed_representation(tmp_path, case):
    engine, provider, clock, state = setup_engine(tmp_path)
    ctx = context(engine, provider, clock)
    data = contract_wire(state["contract"])

    if case == "duplicate_node":
        data["nodes"].append(deepcopy(data["nodes"][0]))
    elif case == "missing_root":
        data["goal_root"] = "missing-node"
    elif case == "unused_node":
        data["nodes"].append({"id": "unused", "kind": "literal", "literal_type": "boolean", "literal_value": "true"})
    elif case == "cycle":
        operator = next(node for node in data["nodes"] if node["kind"] == "operator")
        operator["args"][0] = operator["id"]
    elif case == "ambiguous_node":
        fact = next(node for node in data["nodes"] if node["kind"] == "fact")
        fact["args"] = []
    elif case == "bad_literal":
        literal = next(node for node in data["nodes"] if node["kind"] == "literal")
        literal["literal_type"] = "boolean"
        literal["literal_value"] = "maybe"
    elif case == "duplicate_authority":
        data["authority"].append(deepcopy(data["authority"][0]))
    else:
        data = {"contract_json": "{}", "confidence": .99}

    with pytest.raises(ValueError):
        normalize_wire(data, ctx)


def test_flat_wire_round_trip_is_exact_representation_normalization(tmp_path):
    engine, provider, clock, state = setup_engine(tmp_path)
    spec, confidence = normalize_wire(contract_wire(state["contract"]), context(engine, provider, clock))
    assert spec == state["contract"]
    assert confidence == .99
