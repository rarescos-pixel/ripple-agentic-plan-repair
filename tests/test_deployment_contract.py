from __future__ import annotations
import asyncio, os
import httpx
from ripple.asgi import app


def run(coro): return asyncio.run(coro)


def production_env() -> dict[str, str]:
    return {
        "RIPPLE_ENV":"production",
        "RIPPLE_PUBLIC_BASE_URL":"https://ripple.example",
        "RIPPLE_SERVICE_CLIENT_ID":"svc-prod",
        "RIPPLE_SERVICE_CLIENT_SECRET":"this-is-a-long-random-looking-service-secret-123",
        "RIPPLE_USER_CLIENT_ID":"user-prod",
        "RIPPLE_USER_REDIRECT_URIS":"https://client.example/callback",
        "RIPPLE_DEMO_USER_PASSWORD":"this-is-a-strong-demo-password",
    }


def test_production_readiness_fails_closed_with_test_secrets():
    old=dict(os.environ)
    try:
        os.environ.update({
            "RIPPLE_ENV":"production",
            "RIPPLE_PUBLIC_BASE_URL":"https://ripple.example",
            "RIPPLE_SERVICE_CLIENT_ID":"svc",
            "RIPPLE_SERVICE_CLIENT_SECRET":"ripple-service-secret-test",
            "RIPPLE_USER_CLIENT_ID":"user",
            "RIPPLE_USER_REDIRECT_URIS":"https://client.example/callback",
            "RIPPLE_DEMO_USER_PASSWORD":"ripple-demo-password-test",
        })
        async def case():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
                r=await c.get('/readyz')
                assert r.status_code==503
                assert r.json()['status']=='not_ready'
        run(case())
    finally:
        os.environ.clear(); os.environ.update(old)


def test_production_readiness_reports_non_aws_mode_before_cutover():
    old=dict(os.environ)
    try:
        os.environ.update(production_env())
        for name in (
            "RIPPLE_STATE_BACKEND", "RIPPLE_CHANGE_INTERPRETER", "RIPPLE_TRACE_BACKEND",
            "RIPPLE_DYNAMODB_TABLE", "RIPPLE_BEDROCK_MODEL_ID", "RIPPLE_CLOUDWATCH_LOG_GROUP",
            "RIPPLE_REQUIRE_AWS_RUNTIME",
        ):
            os.environ.pop(name, None)
        async def case():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
                r=await c.get('/readyz')
                assert r.status_code==200
                body=r.json()
                assert body['resource']=='https://ripple.example/mcp'
                assert body['runtime_mode']=='non-aws'
                assert body['structural_aws_runtime'] is False
                assert body['aws_components']==[]
        run(case())
    finally:
        os.environ.clear(); os.environ.update(old)


def test_production_readiness_fails_closed_on_partial_aws_cutover():
    old=dict(os.environ)
    try:
        os.environ.update(production_env())
        os.environ.update({
            "RIPPLE_STATE_BACKEND":"dynamodb",
            "RIPPLE_DYNAMODB_TABLE":"ripple-demo-state",
            "RIPPLE_CHANGE_INTERPRETER":"golden",
            "RIPPLE_TRACE_BACKEND":"none",
        })
        async def case():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
                r=await c.get('/readyz')
                assert r.status_code==503
                assert 'Partial AWS runtime is forbidden' in r.json()['error']
        run(case())
    finally:
        os.environ.clear(); os.environ.update(old)


def test_production_readiness_exposes_non_secret_structural_aws_evidence():
    old=dict(os.environ)
    try:
        os.environ.update(production_env())
        os.environ.update({
            "RIPPLE_STATE_BACKEND":"dynamodb",
            "RIPPLE_DYNAMODB_TABLE":"ripple-demo-state",
            "RIPPLE_CHANGE_INTERPRETER":"bedrock",
            "RIPPLE_BEDROCK_MODEL_ID":"arn:aws:bedrock:eu-central-1:123456789012:application-inference-profile/example",
            "RIPPLE_TRACE_BACKEND":"cloudwatch",
            "RIPPLE_CLOUDWATCH_LOG_GROUP":"/ripple/demo/runtime",
            "RIPPLE_CLOUDWATCH_LOG_STREAM":"runtime",
            "RIPPLE_REQUIRE_AWS_RUNTIME":"true",
            "AWS_REGION":"eu-central-1",
        })
        async def case():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
                r=await c.get('/readyz')
                assert r.status_code==200
                body=r.json()
                assert body['runtime_mode']=='aws-structural'
                assert body['structural_aws_runtime'] is True
                assert body['aws_components']==['dynamodb','bedrock','cloudwatch']
                rendered=r.text
                assert 'ripple-demo-state' not in rendered
                assert '/ripple/demo/runtime' not in rendered
                assert 'application-inference-profile/example' not in rendered
        run(case())
    finally:
        os.environ.clear(); os.environ.update(old)
