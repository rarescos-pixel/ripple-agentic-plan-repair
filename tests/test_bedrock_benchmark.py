from pathlib import Path

from ripple.evaluation.bedrock_benchmark import evaluate_model, load_cases, rank


CASES = Path(__file__).resolve().parents[1] / "fixtures" / "bedrock_normalization_cases.json"


class FakeModelClient:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.last_usage = {}

    def converse(self, **kwargs):
        text = kwargs["messages"][0]["content"][0]["text"]
        self.last_usage = {"inputTokens": 100, "outputTokens": 20}
        if "flight:return" in text:
            node, field, value = "flight:return", "arrival_at", "2026-09-11T18:00:00"
        elif "calendar:client" in text:
            node, field, value = "calendar:client", "start_at", "2026-09-14T13:30:00"
        elif "care:C1" in text:
            node, field, value = "care:C1", "end_at", "2026-09-12T20:00:00"
        elif "delivery:G1" in text:
            node, field, value = "delivery:G1", "start_at", "2026-09-11T20:15:00"
        else:
            node, field, value = "reservation:D1", "start_at", "2026-09-12T19:45:00"
        if self.model_id.endswith("nova-lite-v1:0") and node == "reservation:D1":
            value = "2026-09-12T19:00:00"
        return {
            "output": {"message": {"content": [{"toolUse": {
                "name": "record_change",
                "input": {"node_id": node, "field": field, "new_value": value, "confidence": 0.95},
            }}]}},
            "usage": self.last_usage,
        }


def test_benchmark_quality_dominates_and_usage_is_counted():
    cases = load_cases(CASES)
    lite = evaluate_model("eu.amazon.nova-lite-v1:0", cases, FakeModelClient)
    nova2 = evaluate_model("eu.amazon.nova-2-lite-v1:0", cases, FakeModelClient)
    assert lite.passed == 4
    assert nova2.passed == 5
    assert nova2.input_tokens == 500 and nova2.output_tokens == 100
    assert rank([lite, nova2])[0].model_id == "eu.amazon.nova-2-lite-v1:0"
