from __future__ import annotations

import asyncio

import httpx

from ripple.auth import reset_auth_state
from ripple.mcp_server import app

BASE = "http://testserver"


def run(coro):
    return asyncio.run(coro)


def base_env(monkeypatch):
    reset_auth_state()
    monkeypatch.setenv("RIPPLE_ENV", "test")
    monkeypatch.setenv("RIPPLE_PUBLIC_BASE_URL", BASE)
    monkeypatch.setenv("RIPPLE_SERVICE_CLIENT_ID", "svc")
    monkeypatch.setenv("RIPPLE_SERVICE_CLIENT_SECRET", "secret")
    monkeypatch.setenv("RIPPLE_USER_CLIENT_ID", "user-client")
    monkeypatch.setenv("RIPPLE_USER_REDIRECT_URIS", "https://client.example/callback")
    monkeypatch.setenv("RIPPLE_DEMO_USER_PASSWORD", "ripple-demo-password-test")
    monkeypatch.delenv("RIPPLE_REQUIRE_AWS_RUNTIME", raising=False)
    monkeypatch.delenv("RIPPLE_DYNAMODB_TABLE", raising=False)
    monkeypatch.delenv("RIPPLE_BEDROCK_MODEL_ID", raising=False)
    monkeypatch.delenv("RIPPLE_CLOUDWATCH_LOG_GROUP", raising=False)
    monkeypatch.delenv("RAILWAY_GIT_COMMIT_SHA", raising=False)


async def ready_payload():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url=BASE,
    ) as client:
        response = await client.get("/readyz")
        return response


def test_readyz_reports_non_aws_runtime_without_inventing_source_revision(monkeypatch):
    base_env(monkeypatch)
    monkeypatch.setenv("RIPPLE_STATE_BACKEND", "memory")
    monkeypatch.setenv("RIPPLE_CHANGE_INTERPRETER", "golden")
    monkeypatch.setenv("RIPPLE_TRACE_BACKEND", "none")

    response = run(ready_payload())
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["runtime_mode"] == "non-aws"
    assert payload["structural_aws_runtime"] is False
    assert payload["aws_components"] == []
    assert "source_revision" not in payload


def test_readyz_reports_structural_aws_profile_and_exact_railway_source(monkeypatch):
    base_env(monkeypatch)
    expected_sha = "0123456789abcdef0123456789abcdef01234567"
    monkeypatch.setenv("RAILWAY_GIT_COMMIT_SHA", expected_sha.upper())
    monkeypatch.setenv("RIPPLE_REQUIRE_AWS_RUNTIME", "true")
    monkeypatch.setenv("RIPPLE_STATE_BACKEND", "dynamodb")
    monkeypatch.setenv("RIPPLE_DYNAMODB_TABLE", "ripple-test")
    monkeypatch.setenv("RIPPLE_CHANGE_INTERPRETER", "bedrock")
    monkeypatch.setenv("RIPPLE_BEDROCK_MODEL_ID", "arn:aws:bedrock:eu-central-1:123456789012:application-inference-profile/test")
    monkeypatch.setenv("RIPPLE_TRACE_BACKEND", "cloudwatch")
    monkeypatch.setenv("RIPPLE_CLOUDWATCH_LOG_GROUP", "/ripple/test")
    monkeypatch.setenv("AWS_REGION", "eu-central-1")

    response = run(ready_payload())
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["runtime_mode"] == "aws-structural"
    assert payload["structural_aws_runtime"] is True
    assert payload["aws_components"] == ["dynamodb", "bedrock", "cloudwatch"]
    assert payload["source_revision"] == expected_sha
    assert "RIPPLE_DYNAMODB_TABLE" not in response.text
    assert "RIPPLE_BEDROCK_MODEL_ID" not in response.text
    assert "RIPPLE_CLOUDWATCH_LOG_GROUP" not in response.text


def test_readyz_fails_closed_for_partial_required_aws_profile(monkeypatch):
    base_env(monkeypatch)
    monkeypatch.setenv("RIPPLE_REQUIRE_AWS_RUNTIME", "true")
    monkeypatch.setenv("RIPPLE_STATE_BACKEND", "dynamodb")
    monkeypatch.setenv("RIPPLE_CHANGE_INTERPRETER", "golden")
    monkeypatch.setenv("RIPPLE_TRACE_BACKEND", "none")

    response = run(ready_payload())
    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "not_ready"
    assert "Partial AWS runtime is forbidden" in payload["error"]


def test_readyz_omits_invalid_railway_revision(monkeypatch):
    base_env(monkeypatch)
    monkeypatch.setenv("RIPPLE_STATE_BACKEND", "memory")
    monkeypatch.setenv("RIPPLE_CHANGE_INTERPRETER", "golden")
    monkeypatch.setenv("RIPPLE_TRACE_BACKEND", "none")
    monkeypatch.setenv("RAILWAY_GIT_COMMIT_SHA", "not-a-sha")

    response = run(ready_payload())
    assert response.status_code == 200
    assert "source_revision" not in response.json()
