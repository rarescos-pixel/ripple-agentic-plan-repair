from __future__ import annotations

import json
import os
from urllib.parse import urlparse

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

BASE = "https://api.browserbase.com/v1"
API_KEY = os.getenv("BROWSERBASE_API_KEY", "").strip()
BROKER_TOKEN = os.getenv("BROKER_TOKEN", "").strip()
ALLOWED_FUNCTION_IDS = {
    x.strip() for x in os.getenv("ALLOWED_FUNCTION_IDS", "").split(",") if x.strip()
}
ALLOWED_HOST_SUFFIXES = tuple(
    x.strip().lower() for x in os.getenv(
        "ALLOWED_HOST_SUFFIXES", "amazon.com,aws.amazon.com"
    ).split(",") if x.strip()
)


def _authorized(token: str) -> bool:
    return bool(BROKER_TOKEN) and token == BROKER_TOKEN


def _headers() -> dict[str, str]:
    if not API_KEY:
        raise RuntimeError("BROWSERBASE_API_KEY is not configured")
    return {"X-BB-API-Key": API_KEY, "Content-Type": "application/json"}


def _host_allowed(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    return bool(host) and any(host == s or host.endswith("." + s) for s in ALLOWED_HOST_SUFFIXES)


def _no_store(payload: object, status_code: int = 200) -> JSONResponse:
    r = JSONResponse(payload, status_code=status_code)
    r.headers["Cache-Control"] = "no-store"
    r.headers["Pragma"] = "no-cache"
    return r


async def health(_: Request) -> JSONResponse:
    return _no_store({
        "ok": True,
        "apiKeyConfigured": bool(API_KEY),
        "brokerTokenConfigured": bool(BROKER_TOKEN),
        "functionAllowlistCount": len(ALLOWED_FUNCTION_IDS),
    })


async def build_status(request: Request) -> JSONResponse:
    if not _authorized(request.path_params["token"]):
        return _no_store({"error": "unauthorized"}, 401)
    build_id = request.path_params["build_id"]
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{BASE}/functions/builds/{build_id}", headers=_headers())
    try:
        body = resp.json()
    except Exception:
        body = {"raw": resp.text[:2000]}
    if isinstance(body, dict):
        body = {
            "id": body.get("id"),
            "status": body.get("status"),
            "cause": body.get("cause"),
            "builtFunctions": [
                {
                    "id": f.get("id"),
                    "name": f.get("name"),
                    "versionId": (f.get("createdVersion") or {}).get("id"),
                }
                for f in (body.get("builtFunctions") or [])
                if isinstance(f, dict)
            ],
        }
    return _no_store(body, resp.status_code)


async def invocation_status(request: Request) -> JSONResponse:
    if not _authorized(request.path_params["token"]):
        return _no_store({"error": "unauthorized"}, 401)
    invocation_id = request.path_params["invocation_id"]
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{BASE}/functions/invocations/{invocation_id}", headers=_headers())
    try:
        body = resp.json()
    except Exception:
        body = {"raw": resp.text[:4000]}
    return _no_store(body, resp.status_code)


async def invoke_readonly(request: Request) -> JSONResponse:
    if not _authorized(request.path_params["token"]):
        return _no_store({"error": "unauthorized"}, 401)

    q = request.query_params
    function_id = q.get("function_id", "").strip()
    target = q.get("url", "").strip()
    selector = q.get("selector", "h1").strip() or "h1"
    action = q.get("action", "readText").strip() or "readText"

    if not function_id or function_id not in ALLOWED_FUNCTION_IDS:
        return _no_store({"error": "function_not_allowed"}, 403)
    if not target or not _host_allowed(target):
        return _no_store({"error": "target_not_allowed"}, 403)
    if action not in {"readText", "assertTitle", "assertUrl"}:
        return _no_store({"error": "action_not_allowed"}, 403)

    if action == "readText":
        steps = [{"action": "readText", "selector": selector, "timeoutMs": 30000}]
    elif action == "assertTitle":
        contains = q.get("contains", "")
        steps = [{"action": "assertTitle", "contains": contains, "timeoutMs": 30000}]
    else:
        contains = q.get("contains", "")
        steps = [{"action": "assertUrl", "contains": contains, "timeoutMs": 30000}]

    payload = {
        "params": {
            "url": target,
            "waitUntil": "domcontentloaded",
            "timeoutMs": 30000,
            "sensitive": True,
            "allowSensitiveOutput": True,
            "steps": steps,
        }
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{BASE}/functions/{function_id}/invoke",
            headers=_headers(),
            content=json.dumps(payload),
        )
    try:
        body = resp.json()
    except Exception:
        body = {"raw": resp.text[:4000]}
    return _no_store(body, resp.status_code)


app = Starlette(routes=[
    Route("/healthz", health, methods=["GET"]),
    Route("/_/{token}/build/{build_id}", build_status, methods=["GET"]),
    Route("/_/{token}/invocation/{invocation_id}", invocation_status, methods=["GET"]),
    Route("/_/{token}/invoke", invoke_readonly, methods=["GET"]),
])
