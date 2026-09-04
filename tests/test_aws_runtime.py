import pytest

from ripple.aws.profile import current_runtime_profile, validate_runtime_profile
from ripple.aws.runtime import NoopTraceSink, build_change_interpreter, build_trace_sink
from ripple.golden import build_golden
from ripple.orchestration.agent import GoldenChangeInterpreter


def _clear_aws_runtime(monkeypatch):
    for name in (
        "RIPPLE_STATE_BACKEND",
        "RIPPLE_CHANGE_INTERPRETER",
        "RIPPLE_TRACE_BACKEND",
        "RIPPLE_DYNAMODB_TABLE",
        "RIPPLE_BEDROCK_MODEL_ID",
        "RIPPLE_CLOUDWATCH_LOG_GROUP",
        "RIPPLE_CLOUDWATCH_LOG_STREAM",
        "RIPPLE_REQUIRE_AWS_RUNTIME",
        "AWS_REGION",
    ):
        monkeypatch.delenv(name, raising=False)


def test_default_runtime_preserves_verified_golden_path(monkeypatch):
    _clear_aws_runtime(monkeypatch)
    monkeypatch.setenv("RIPPLE_ENV", "development")
    assert isinstance(build_change_interpreter(), GoldenChangeInterpreter)
    assert isinstance(build_trace_sink(), NoopTraceSink)


def test_bedrock_mode_requires_explicit_model_id(monkeypatch):
    _clear_aws_runtime(monkeypatch)
    monkeypatch.setenv("RIPPLE_ENV", "development")
    monkeypatch.setenv("RIPPLE_CHANGE_INTERPRETER", "bedrock")
    with pytest.raises(RuntimeError, match="RIPPLE_BEDROCK_MODEL_ID"):
        build_change_interpreter()


def test_cloudwatch_mode_requires_log_group(monkeypatch):
    _clear_aws_runtime(monkeypatch)
    monkeypatch.setenv("RIPPLE_ENV", "development")
    monkeypatch.setenv("RIPPLE_TRACE_BACKEND", "cloudwatch")
    with pytest.raises(RuntimeError, match="RIPPLE_CLOUDWATCH_LOG_GROUP"):
        build_trace_sink()


def test_unknown_backends_fail_closed(monkeypatch):
    _clear_aws_runtime(monkeypatch)
    monkeypatch.setenv("RIPPLE_ENV", "development")
    monkeypatch.setenv("RIPPLE_CHANGE_INTERPRETER", "magic")
    with pytest.raises(RuntimeError, match="Unsupported"):
        build_change_interpreter()
    monkeypatch.setenv("RIPPLE_CHANGE_INTERPRETER", "golden")
    monkeypatch.setenv("RIPPLE_TRACE_BACKEND", "magic")
    with pytest.raises(RuntimeError, match="Unsupported"):
        build_trace_sink()


def test_production_allows_verified_non_aws_runtime_until_cutover(monkeypatch):
    _clear_aws_runtime(monkeypatch)
    monkeypatch.setenv("RIPPLE_ENV", "production")
    profile = validate_runtime_profile()
    assert profile.environment == "production"
    assert profile.full_aws_runtime is False


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("RIPPLE_STATE_BACKEND", "dynamodb"),
        ("RIPPLE_CHANGE_INTERPRETER", "bedrock"),
        ("RIPPLE_TRACE_BACKEND", "cloudwatch"),
    ],
)
def test_production_forbids_partial_aws_runtime(monkeypatch, name, value):
    _clear_aws_runtime(monkeypatch)
    monkeypatch.setenv("RIPPLE_ENV", "production")
    monkeypatch.setenv(name, value)
    with pytest.raises(RuntimeError, match="Partial AWS runtime"):
        validate_runtime_profile()


def test_canonical_builder_rejects_partial_aws_before_backend_construction(monkeypatch):
    _clear_aws_runtime(monkeypatch)
    monkeypatch.setenv("RIPPLE_ENV", "production")
    monkeypatch.setenv("RIPPLE_STATE_BACKEND", "dynamodb")
    monkeypatch.setenv("RIPPLE_DYNAMODB_TABLE", "must-not-be-opened")
    with pytest.raises(RuntimeError, match="Partial AWS runtime"):
        build_golden()


def test_explicit_aws_runtime_lock_requires_all_three_components(monkeypatch):
    _clear_aws_runtime(monkeypatch)
    monkeypatch.setenv("RIPPLE_ENV", "development")
    monkeypatch.setenv("RIPPLE_REQUIRE_AWS_RUNTIME", "true")
    with pytest.raises(RuntimeError, match="Partial AWS runtime"):
        validate_runtime_profile()


def test_full_aws_runtime_profile_requires_resource_bindings(monkeypatch):
    _clear_aws_runtime(monkeypatch)
    monkeypatch.setenv("RIPPLE_ENV", "production")
    monkeypatch.setenv("RIPPLE_STATE_BACKEND", "dynamodb")
    monkeypatch.setenv("RIPPLE_CHANGE_INTERPRETER", "bedrock")
    monkeypatch.setenv("RIPPLE_TRACE_BACKEND", "cloudwatch")
    with pytest.raises(RuntimeError, match="configuration is incomplete"):
        validate_runtime_profile()


def test_full_aws_runtime_profile_is_accepted_only_when_complete(monkeypatch):
    _clear_aws_runtime(monkeypatch)
    monkeypatch.setenv("RIPPLE_ENV", "production")
    monkeypatch.setenv("RIPPLE_REQUIRE_AWS_RUNTIME", "true")
    monkeypatch.setenv("RIPPLE_STATE_BACKEND", "dynamodb")
    monkeypatch.setenv("RIPPLE_CHANGE_INTERPRETER", "bedrock")
    monkeypatch.setenv("RIPPLE_TRACE_BACKEND", "cloudwatch")
    monkeypatch.setenv("RIPPLE_DYNAMODB_TABLE", "ripple-state-live")
    monkeypatch.setenv("RIPPLE_BEDROCK_MODEL_ID", "arn:aws:bedrock:eu-central-1:123456789012:application-inference-profile/ripple")
    monkeypatch.setenv("RIPPLE_CLOUDWATCH_LOG_GROUP", "/ripple/runtime")
    monkeypatch.setenv("RIPPLE_CLOUDWATCH_LOG_STREAM", "railway")
    monkeypatch.setenv("AWS_REGION", "eu-central-1")
    profile = validate_runtime_profile()
    assert profile.full_aws_runtime is True
    assert profile.require_aws_runtime is True
    assert profile.aws_region == "eu-central-1"


def test_invalid_runtime_lock_flag_fails_closed(monkeypatch):
    _clear_aws_runtime(monkeypatch)
    monkeypatch.setenv("RIPPLE_REQUIRE_AWS_RUNTIME", "maybe")
    with pytest.raises(RuntimeError, match="boolean flag"):
        current_runtime_profile()
