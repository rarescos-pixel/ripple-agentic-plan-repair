from __future__ import annotations

import secrets
import time
from typing import Dict

from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response

from ripple.webapp import DemoController, INDEX_HTML

DEMO_COOKIE = "ripple_demo_sid"
DEMO_TTL_SECONDS = 3600
DEMO_MAX_SESSIONS = 250

# The judge demo is deliberately isolated from the authenticated MCP session map.
# It drives deterministic simulated provider adapters only; public MCP transport
# proof remains a separate authenticated evidence path.
_DEMO_SESSIONS: Dict[str, tuple[DemoController, float]] = {}


def _cleanup_sessions() -> None:
    cutoff = time.time() - DEMO_TTL_SECONDS
    expired = [sid for sid, (_, last_seen) in _DEMO_SESSIONS.items() if last_seen < cutoff]
    for sid in expired:
        _DEMO_SESSIONS.pop(sid, None)
    if len(_DEMO_SESSIONS) <= DEMO_MAX_SESSIONS:
        return
    oldest = sorted(_DEMO_SESSIONS.items(), key=lambda item: item[1][1])
    for sid, _ in oldest[: len(_DEMO_SESSIONS) - DEMO_MAX_SESSIONS]:
        _DEMO_SESSIONS.pop(sid, None)


def _controller_for(request: Request) -> tuple[str, DemoController, bool]:
    _cleanup_sessions()
    sid = request.cookies.get(DEMO_COOKIE, "")
    if sid and sid in _DEMO_SESSIONS:
        controller, _ = _DEMO_SESSIONS[sid]
        _DEMO_SESSIONS[sid] = (controller, time.time())
        return sid, controller, False
    sid = secrets.token_urlsafe(18)
    controller = DemoController()
    _DEMO_SESSIONS[sid] = (controller, time.time())
    return sid, controller, True


def _set_demo_cookie(response: Response, sid: str) -> None:
    response.set_cookie(
        DEMO_COOKIE,
        sid,
        max_age=DEMO_TTL_SECONDS,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/demo",
    )


def public_demo_html() -> str:
    """Mount the local demo under /demo without changing its standalone server."""
    return INDEX_HTML.replace("'/api/", "'/demo/api/")


async def handle_judge_demo(scope, receive) -> Response | None:
    if scope.get("type") != "http":
        return None
    path = scope.get("path", "")
    if path not in {
        "/demo",
        "/demo/",
        "/demo/api/evidence",
        "/demo/api/propose",
        "/demo/api/approve",
        "/demo/api/replay",
        "/demo/api/reset",
    }:
        return None

    request = Request(scope, receive)
    method = scope.get("method", "GET").upper()

    if path in {"/demo", "/demo/"}:
        if method != "GET":
            return Response(status_code=405, headers={"Allow": "GET"})
        sid, _, _ = _controller_for(request)
        response = HTMLResponse(
            public_demo_html(),
            headers={
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Content-Security-Policy": "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'",
            },
        )
        _set_demo_cookie(response, sid)
        return response

    if path == "/demo/api/evidence":
        if method != "GET":
            return Response(status_code=405, headers={"Allow": "GET"})
        sid, controller, _ = _controller_for(request)
        response = JSONResponse(controller.evidence())
        _set_demo_cookie(response, sid)
        return response

    if method != "POST":
        return Response(status_code=405, headers={"Allow": "POST"})

    sid, controller, _ = _controller_for(request)
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ValueError("JSON body must be an object")
        if path == "/demo/api/propose":
            utterance = str(body.get("utterance", "")).strip()
            if not utterance:
                raise ValueError("utterance is required")
            payload = controller.propose(utterance)
        elif path == "/demo/api/approve":
            payload = controller.approve(body)
        elif path == "/demo/api/replay":
            payload = controller.replay()
        elif path == "/demo/api/reset":
            payload = controller.reset()
        else:  # guarded by route set above
            return JSONResponse({"error": "not_found"}, status_code=404)
    except Exception as exc:
        response = JSONResponse({"error": str(exc)}, status_code=400)
        _set_demo_cookie(response, sid)
        return response

    response = JSONResponse(payload)
    _set_demo_cookie(response, sid)
    return response
