import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from ripple.orchestration.bedrock_interpreter import BedrockChangeInterpreter
from ripple.policy.cost import ModelBudget


class FakeBedrock:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        return {"output": {"message": {"content": [{"toolUse": {"name": "record_change", "toolUseId": "t1", "input": self.payload}}]}}}


def context():
    return {
        "allowed_nodes": {"flight:return": {"arrival_at": "2026-09-10T21:00:00"}},
        "allowed_fields": {"flight:return": ["arrival_at"]},
        "minimum_confidence": 0.8,
    }


def test_bedrock_tool_call_normalizes_only_changed_fact():
    fake = FakeBedrock({"node_id": "flight:return", "field": "arrival_at", "new_value": "2026-09-11T18:00:00", "confidence": 0.98})
    event = BedrockChangeInterpreter(fake).interpret("Our flight was cancelled; we land tomorrow at six.", context())
    assert event.node_id == "flight:return"
    assert event.old_value == "2026-09-10T21:00:00"  # authoritative context, not model
    assert event.new_value == "2026-09-11T18:00:00"
    assert event.id.startswith("change:bedrock:")
    assert event.correlation_id.startswith("bedrock:")
    assert fake.calls[0]["requestMetadata"]["ripple_correlation_id"] == event.correlation_id
    assert len(fake.calls) == 1
    assert fake.calls[0]["inferenceConfig"] == {"maxTokens": 256, "temperature": 0}
    assert fake.calls[0]["toolConfig"]["toolChoice"]["tool"]["name"] == "record_change"


def test_bedrock_change_identity_is_stable_for_same_canonical_transition():
    payload = {"node_id": "flight:return", "field": "arrival_at", "new_value": "2026-09-11T18:00:00", "confidence": 0.98}
    first = BedrockChangeInterpreter(FakeBedrock(payload)).interpret("We land tomorrow at six", context())
    second = BedrockChangeInterpreter(FakeBedrock(payload)).interpret("Arrival is 18:00 tomorrow", context())
    assert first.id == second.id


def test_bedrock_trace_identity_is_unique_without_changing_replay_identity():
    payload = {"node_id": "flight:return", "field": "arrival_at", "new_value": "2026-09-11T18:00:00", "confidence": 0.98}
    first = BedrockChangeInterpreter(FakeBedrock(payload)).interpret("We land tomorrow at six", context())
    second = BedrockChangeInterpreter(FakeBedrock(payload)).interpret("Arrival is 18:00 tomorrow", context())
    assert first.id == second.id
    assert first.correlation_id != second.correlation_id
    assert first.correlation_id.startswith("bedrock:")
    assert second.correlation_id.startswith("bedrock:")


def test_explicit_correlation_id_remains_authoritative():
    payload = {"node_id": "flight:return", "field": "arrival_at", "new_value": "2026-09-11T18:00:00", "confidence": 0.98}
    fake = FakeBedrock(payload)
    ctx = context()
    ctx["correlation_id"] = "judge-trace-123"
    event = BedrockChangeInterpreter(fake).interpret("We land tomorrow at six", ctx)
    assert event.correlation_id == "judge-trace-123"
    assert fake.calls[0]["requestMetadata"]["ripple_correlation_id"] == "judge-trace-123"


def test_bedrock_distinct_changes_get_distinct_idempotency_identity():
    first_payload = {"node_id": "flight:return", "field": "arrival_at", "new_value": "2026-09-11T18:00:00", "confidence": 0.98}
    second_payload = {"node_id": "flight:return", "field": "arrival_at", "new_value": "2026-09-11T23:55:00", "confidence": 0.98}
    first = BedrockChangeInterpreter(FakeBedrock(first_payload)).interpret("We land tomorrow at six", context())
    second = BedrockChangeInterpreter(FakeBedrock(second_payload)).interpret("We now land tomorrow at 23:55", context())
    assert first.id != second.id


def test_explicit_change_id_remains_authoritative():
    payload = {"node_id": "flight:return", "field": "arrival_at", "new_value": "2026-09-11T18:00:00", "confidence": 0.98}
    ctx = context()
    ctx["change_id"] = "change:external-authoritative"
    event = BedrockChangeInterpreter(FakeBedrock(payload)).interpret("We land tomorrow at six", ctx)
    assert event.id == "change:external-authoritative"


def test_bedrock_cannot_inject_unknown_node():
    fake = FakeBedrock({"node_id": "bank:account", "field": "balance", "new_value": "0", "confidence": 0.99})
    with pytest.raises(ValueError, match="outside canonical context"):
        BedrockChangeInterpreter(fake).interpret("Do something else", context())


def test_low_confidence_does_not_reach_planner():
    fake = FakeBedrock({"node_id": "flight:return", "field": "arrival_at", "new_value": "2026-09-11T18:00:00", "confidence": 0.40})
    with pytest.raises(ValueError, match="below execution-planning threshold"):
        BedrockChangeInterpreter(fake).interpret("Maybe tomorrow?", context())


def test_input_budget_blocks_oversized_prompt_before_model_call():
    fake = FakeBedrock({"node_id": "flight:return", "field": "arrival_at", "new_value": "2026-09-11T18:00:00", "confidence": 0.99})
    interpreter = BedrockChangeInterpreter(fake, budget=ModelBudget(max_input_chars=100))
    with pytest.raises(ValueError, match="cost budget"):
        interpreter.interpret("x" * 500, context())
    assert fake.calls == []
