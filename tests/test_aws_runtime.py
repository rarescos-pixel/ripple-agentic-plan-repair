import pytest

from ripple.aws.runtime import NoopTraceSink, build_change_interpreter, build_trace_sink
from ripple.orchestration.agent import GoldenChangeInterpreter


def test_default_runtime_preserves_verified_golden_path(monkeypatch):
    monkeypatch.delenv("RIPPLE_CHANGE_INTERPRETER", raising=False)
    monkeypatch.delenv("RIPPLE_TRACE_BACKEND", raising=False)
    assert isinstance(build_change_interpreter(), GoldenChangeInterpreter)
    assert isinstance(build_trace_sink(), NoopTraceSink)


def test_bedrock_mode_requires_explicit_model_id(monkeypatch):
    monkeypatch.setenv("RIPPLE_CHANGE_INTERPRETER", "bedrock")
    monkeypatch.delenv("RIPPLE_BEDROCK_MODEL_ID", raising=False)
    with pytest.raises(RuntimeError, match="RIPPLE_BEDROCK_MODEL_ID"):
        build_change_interpreter()


def test_cloudwatch_mode_requires_log_group(monkeypatch):
    monkeypatch.setenv("RIPPLE_TRACE_BACKEND", "cloudwatch")
    monkeypatch.delenv("RIPPLE_CLOUDWATCH_LOG_GROUP", raising=False)
    with pytest.raises(RuntimeError, match="RIPPLE_CLOUDWATCH_LOG_GROUP"):
        build_trace_sink()


def test_unknown_backends_fail_closed(monkeypatch):
    monkeypatch.setenv("RIPPLE_CHANGE_INTERPRETER", "magic")
    with pytest.raises(RuntimeError, match="Unsupported"):
        build_change_interpreter()
    monkeypatch.setenv("RIPPLE_TRACE_BACKEND", "magic")
    with pytest.raises(RuntimeError, match="Unsupported"):
        build_trace_sink()
