from __future__ import annotations
import asyncio, os
import httpx
from ripple.mcp_server import app


def run(coro): return asyncio.run(coro)


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


def test_production_readiness_accepts_https_and_real_secrets():
    old=dict(os.environ)
    try:
        os.environ.update({
            "RIPPLE_ENV":"production",
            "RIPPLE_PUBLIC_BASE_URL":"https://ripple.example",
            "RIPPLE_SERVICE_CLIENT_ID":"svc-prod",
            "RIPPLE_SERVICE_CLIENT_SECRET":"this-is-a-long-random-looking-service-secret-123",
            "RIPPLE_USER_CLIENT_ID":"user-prod",
            "RIPPLE_USER_REDIRECT_URIS":"https://client.example/callback",
            "RIPPLE_DEMO_USER_PASSWORD":"this-is-a-strong-demo-password",
        })
        async def case():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
                r=await c.get('/readyz')
                assert r.status_code==200
                assert r.json()['resource']=='https://ripple.example/mcp'
        run(case())
    finally:
        os.environ.clear(); os.environ.update(old)
