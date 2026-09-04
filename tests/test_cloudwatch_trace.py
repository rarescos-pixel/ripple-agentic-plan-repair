import json
import pytest

from ripple.observability.cloudwatch import CloudWatchTraceSink


class FakeLogs:
    def __init__(self):
        self.calls = []

    def put_log_events(self, **kwargs):
        self.calls.append(kwargs)
        return {"nextSequenceToken": "ignored-by-current-api"}


def test_cloudwatch_trace_is_structured_redacted_and_has_no_sequence_token():
    client = FakeLogs()
    sink = CloudWatchTraceSink(client, "/ripple/demo/runtime", "runtime")
    envelope = sink.emit(
        "plan.approved",
        correlation_id="corr-1",
        payload={
            "plan_id": "plan-1",
            "authorization": "Bearer do-not-log",
            "nested": {"client_secret": "also-do-not-log", "safe": 42},
        },
        timestamp_ms=1234,
    )
    assert envelope["schema"] == "ripple.trace.v1"
    call = client.calls[0]
    assert "sequenceToken" not in call
    assert call["logGroupName"] == "/ripple/demo/runtime"
    body = json.loads(call["logEvents"][0]["message"])
    assert body["payload"]["authorization"] == "[REDACTED]"
    assert body["payload"]["nested"]["client_secret"] == "[REDACTED]"
    assert body["payload"]["nested"]["safe"] == 42


def test_cloudwatch_trace_rejects_oversized_message():
    sink = CloudWatchTraceSink(FakeLogs(), "g", "s", max_message_bytes=100)
    with pytest.raises(ValueError, match="exceeds"):
        sink.emit("event", correlation_id="c", payload={"data": "x" * 500})
