from __future__ import annotations

import json
import os
import secrets
import time
from dataclasses import asdict
from typing import Any, Dict
from urllib.parse import urlparse

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from ripple.aws.runtime import build_change_interpreter, build_trace_sink
from ripple.domain.models import Approval
from ripple.auth import (
    authenticate_request, authorization_server_metadata, authorize,
    protected_resource_metadata, token, load_auth_config,
)
from ripple.golden import build_golden
from ripple.orchestration.agent import RippleAgent
from ripple.orchestration.session import RippleSession
from ripple.presentation import build_repair_card
from ripple.presentation.mcp_app import (
    REPAIR_CARD_RESOURCE_URI,
    repair_card_resource_contents,
    repair_card_resource_descriptor,
)

PROTOCOL_VERSION = "2025-11-25"
SERVER_INFO = {"name": "ripple-plan-repair", "version": "1.5.0"}
DEFAULT_ALLOWED_ORIGINS = {"http://127.0.0.1", "http://localhost", "https://127.0.0.1", "https://localhost"}


def _tool(
    name: str,
    description: str,
    properties: Dict[str, Any],
    required: list[str],
    *,
    read_only: bool = False,
    destructive: bool = False,
    ui_resource_uri: str | None = None,
) -> Dict[str, Any]:
    tool: Dict[str, Any] = {
        "name": name,
        "description": description,
        "inputSchema": {"type": "object", "properties": properties, "required": required, "additionalProperties": False},
        "annotations": {
            "readOnlyHint": read_only,
            "destructiveHint": destructive,
            "idempotentHint": name in {"preview_repair_plan", "get_repair_status", "execute_repair_plan"},
            "openWorldHint": False,
        },
    }
    if ui_resource_uri:
        tool["_meta"] = {
            "ui": {
                "resourceUri": ui_resource_uri,
                "visibility": ["model", "app"],
            }
        }
    return tool


TOOLS = [
    _tool("record_change", "Record one user-reported flight-arrival change. This tool does not execute repairs.",
          {"utterance": {"type": "string", "description": "Example: Our flight home was cancelled. We'll land tomorrow at 18:00."}}, ["utterance"]),
    _tool(
        "preview_repair_plan",
        "Return the downstream repair plan, money-first Repair Card, and exact approval snapshot. No external writes occur.",
        {},
        [],
        read_only=True,
        ui_resource_uri=REPAIR_CARD_RESOURCE_URI,
    ),
    _tool("approve_repair_plan", "Persist explicit user approval of the exact snapshot previously shown by the client. The client must only call this after human confirmation.",
          {"plan_id": {"type": "string"}, "plan_version": {"type": "integer"}, "snapshot_hash": {"type": "string"}, "max_total_cost": {"type": "number"}, "external_people_notified": {"type": "integer"}, "user_confirmed": {"type": "boolean", "const": True}},
          ["plan_id", "plan_version", "snapshot_hash", "max_total_cost", "external_people_notified", "user_confirmed"]),
    _tool("execute_repair_plan", "Execute only a previously approved exact plan snapshot. Replay is idempotent and consults persisted authoritative receipts when a durable state backend is configured.", {}, [], destructive=True),
    _tool("get_repair_status", "Return current phase, receipts, unique external writes, and unresolved items.", {}, [], read_only=True),
]

APP_RESOURCES = [repair_card_resource_descriptor()]


class McpRippleSession:
    def __init__(self) -> None:
        self.created_at = time.time()
        self.last_seen_at = self.created_at
        self.user_subject: str | None = None
        _, tools, planner, executor, _ = build_golden()
        self.tools = tools
        self.trace = build_trace_sink()
        self.agent = RippleAgent(build_change_interpreter(), planner)
        self.session = RippleSession(self.agent, executor)
        self.proposal = None
        self.approval: Approval | None = None
        self.receipts = []
        self.initialized = False

    @staticmethod
    def _context() -> Dict[str, Any]:
        return {"old_arrival_at": "2026-09-10T21:00:00"}

    def _trace(self, event_type: str, payload: Dict[str, Any]) -> None:
        correlation_id = (
            self.proposal.change.correlation_id
            if self.proposal is not None
            else f"session:{int(self.created_at * 1000)}"
        )
        self.trace.emit(event_type, correlation_id=correlation_id, payload=payload)

    def record_change(self, utterance: str) -> Dict[str, Any]:
        self.proposal = self.session.propose(utterance, self._context())
        self.approval = None
        self.receipts = []
        change = self.proposal.change
        payload = {"change": asdict(change), "phase": "recorded", "writes": len(self.tools.execution_log)}
        self._trace("change.recorded", {
            "node_id": change.node_id,
            "field": change.field,
            "confidence": change.confidence,
            "source": change.source,
        })
        return payload

    def preview(self) -> Dict[str, Any]:
        if self.proposal is None:
            raise ValueError("record_change must be called first")
        p = self.proposal.plan
        payload = {
            "phase": "proposal",
            "spoken_summary": self.proposal.spoken_summary,
            "repair_card": build_repair_card(p),
            "plan": {
                "id": p.id, "version": p.version, "snapshot_hash": p.snapshot_hash(),
                "impact_count": len(p.impacts), "action_count": len(p.actions),
                "total_added_cost": p.total_added_cost, "total_avoidable_loss": p.total_avoidable_loss,
                "net_direct_cash_preserved": p.net_direct_cash_preserved,
                "external_people_notified": p.external_people_notified,
                "unresolved_items": list(p.unresolved_items),
            },
            "approval_snapshot": {
                "plan_id": p.id, "plan_version": p.version, "snapshot_hash": p.snapshot_hash(),
                "max_total_cost": p.total_added_cost, "external_people_notified": p.external_people_notified,
            },
            "writes_before_approval": len(self.tools.execution_log),
        }
        self._trace("plan.previewed", {
            "plan_id": p.id,
            "plan_version": p.version,
            "snapshot_hash_prefix": p.snapshot_hash()[:12],
            "impacts": len(p.impacts),
            "actions": len(p.actions),
            "added_cost": p.total_added_cost,
            "avoidable_loss": p.total_avoidable_loss,
            "net_preserved": p.net_direct_cash_preserved,
            "writes": len(self.tools.execution_log),
        })
        return payload

    def approve(self, a: Dict[str, Any]) -> Dict[str, Any]:
        if self.proposal is None:
            raise ValueError("preview_repair_plan must be called first")
        if a.get("user_confirmed") is not True:
            raise ValueError("Explicit user confirmation is required")
        approval = Approval(
            plan_id=str(a["plan_id"]), plan_version=int(a["plan_version"]),
            max_total_cost=float(a["max_total_cost"]), external_people_notified=int(a["external_people_notified"]),
            plan_snapshot_hash=str(a["snapshot_hash"]), actor="user",
        )
        self.session.record_approval(self.proposal, approval)
        self.approval = approval
        self._trace("plan.approved", {
            "plan_id": approval.plan_id,
            "plan_version": approval.plan_version,
            "snapshot_hash_prefix": approval.plan_snapshot_hash[:12],
            "max_total_cost": approval.max_total_cost,
            "external_people_notified": approval.external_people_notified,
            "writes": len(self.tools.execution_log),
        })
        return {
            "phase": "approved",
            "snapshot_hash": approval.plan_snapshot_hash,
            "approval_persisted": True,
            "writes": len(self.tools.execution_log),
        }

    def execute(self) -> Dict[str, Any]:
        if self.proposal is None or self.approval is None:
            raise ValueError("An exact approved plan is required before execution")
        result = self.session.execute_with_approval(self.proposal, self.approval)
        self.receipts = result.receipts
        payload = {
            "phase": "executed", "plan_status": self.proposal.plan.status,
            "receipt_count": len(self.receipts),
            "deduplicated": sum(1 for r in self.receipts if r.status == "deduplicated"),
            "unique_external_writes": len(self.tools.execution_log),
            "receipts": [asdict(r) for r in self.receipts],
        }
        self._trace("plan.executed", {
            "plan_id": self.proposal.plan.id,
            "plan_status": self.proposal.plan.status,
            "receipt_count": len(self.receipts),
            "executed": sum(1 for r in self.receipts if r.status == "executed"),
            "deduplicated": sum(1 for r in self.receipts if r.status == "deduplicated"),
            "failed": sum(1 for r in self.receipts if r.status == "failed"),
            "unique_external_writes": len(self.tools.execution_log),
        })
        return payload

    def status(self) -> Dict[str, Any]:
        return {
            "phase": "executed" if self.receipts else "approved" if self.approval else "proposal" if self.proposal else "idle",
            "approved_snapshot_hash": self.approval.plan_snapshot_hash if self.approval else None,
            "receipt_count": len(self.receipts),
            "unique_external_writes": len(self.tools.execution_log),
            "unresolved_items": list(self.proposal.plan.unresolved_items) if self.proposal else [],
        }


SESSIONS: Dict[str, McpRippleSession] = {}


def _rpc_error(req_id: Any, code: int, message: str, data: Any = None) -> Dict[str, Any]:
    error: Dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": req_id, "error": error}


def _rpc_result(req_id: Any, result: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _allowed_origins() -> set[str]:
    raw = os.getenv("RIPPLE_ALLOWED_ORIGINS", "")
    if raw.strip():
        return {x.strip().rstrip("/") for x in raw.split(",") if x.strip()}
    return set(DEFAULT_ALLOWED_ORIGINS)


def _valid_origin(request: Request) -> bool:
    origin = request.headers.get("origin")
    if not origin:
        return True
    try:
        parsed = urlparse(origin)
    except ValueError:
        return False
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    if parsed.hostname in {"127.0.0.1", "localhost", "::1"}:
        return True
    normalized = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
    return normalized in _allowed_origins()


def _unauthorized(req_id: Any = None) -> JSONResponse:
    return JSONResponse(_rpc_error(req_id, -32003, "Unauthorized"), status_code=401)


def _authenticate_any(request: Request, scopes: tuple[str, ...]):
    for scope in scopes:
        rec = authenticate_request(request, [scope])
        if rec:
            return rec
    return None


def _cleanup_sessions() -> None:
    ttl = int(os.getenv("RIPPLE_SESSION_TTL_SECONDS", "3600"))
    cutoff = time.time() - ttl
    for sid in [sid for sid, sess in SESSIONS.items() if sess.last_seen_at < cutoff]:
        SESSIONS.pop(sid, None)


def _accepts_streamable(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "application/json" in accept and "text/event-stream" in accept


def _tool_result(payload: Dict[str, Any], *, is_error: bool = False, ui_resource_uri: str | None = None) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "content": [{"type": "text", "text": json.dumps(payload, sort_keys=True, default=str)}],
        "structuredContent": payload,
        "isError": is_error,
    }
    if ui_resource_uri:
        result["_meta"] = {"ui": {"resourceUri": ui_resource_uri}}
    return result


async def mcp_post(request: Request) -> Response:
    if not _valid_origin(request):
        return JSONResponse(_rpc_error(None, -32000, "Invalid Origin"), status_code=403)
    if not _accepts_streamable(request):
        return JSONResponse(_rpc_error(None, -32600, "Accept must include application/json and text/event-stream"), status_code=406)
    if "application/json" not in request.headers.get("content-type", ""):
        return JSONResponse(_rpc_error(None, -32600, "Content-Type must be application/json"), status_code=415)
    try:
        msg = await request.json()
    except Exception:
        return JSONResponse(_rpc_error(None, -32700, "Parse error"), status_code=400)
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
        return JSONResponse(_rpc_error(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request"), status_code=400)

    method, req_id = msg["method"], msg.get("id")
    _cleanup_sessions()
    if method == "initialize":
        principal = _authenticate_any(request, ("mcp:service", "mcp:tools"))
        if principal is None:
            return _unauthorized(req_id)
        max_sessions = int(os.getenv("RIPPLE_MAX_SESSIONS", "1000"))
        if len(SESSIONS) >= max_sessions:
            return JSONResponse(_rpc_error(req_id, -32004, "Session capacity reached"), status_code=503)
        params = msg.get("params") or {}
        client_version = params.get("protocolVersion")
        negotiated = PROTOCOL_VERSION if client_version != PROTOCOL_VERSION else client_version
        sid = secrets.token_urlsafe(24)
        sess = McpRippleSession()
        SESSIONS[sid] = sess
        result = {
            "protocolVersion": negotiated,
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": False},
            },
            "serverInfo": SERVER_INFO,
            "instructions": "Ripple repairs downstream commitments. Show preview_repair_plan and its Repair Card to the user before calling approve_repair_plan; execute only after explicit human confirmation.",
        }
        response = JSONResponse(_rpc_result(req_id, result))
        response.headers["MCP-Session-Id"] = sid
        return response

    if request.headers.get("mcp-protocol-version") != PROTOCOL_VERSION:
        return JSONResponse(_rpc_error(req_id, -32600, "Unsupported or missing MCP-Protocol-Version"), status_code=400)
    sid = request.headers.get("mcp-session-id")
    if not sid:
        return JSONResponse(_rpc_error(req_id, -32001, "Missing MCP-Session-Id"), status_code=400)
    sess = SESSIONS.get(sid)
    if sess is None:
        return JSONResponse(_rpc_error(req_id, -32001, "Unknown or terminated MCP-Session-Id"), status_code=404)
    sess.last_seen_at = time.time()

    if method == "tools/call":
        principal = authenticate_request(request, ["mcp:tools"])
        if principal is None:
            return _unauthorized(req_id)
        if sess.user_subject is None:
            sess.user_subject = principal.subject
        elif principal.subject != sess.user_subject:
            return _unauthorized(req_id)
    else:
        principal = _authenticate_any(request, ("mcp:service", "mcp:tools"))
        if principal is None:
            return _unauthorized(req_id)

    if req_id is None:
        if method == "notifications/initialized":
            sess.initialized = True
            return Response(status_code=202)
        return Response(status_code=202)

    if not sess.initialized and method != "ping":
        return JSONResponse(_rpc_error(req_id, -32002, "Session not initialized"), status_code=400)

    if method == "ping":
        return JSONResponse(_rpc_result(req_id, {}))
    if method == "tools/list":
        return JSONResponse(_rpc_result(req_id, {"tools": TOOLS}))
    if method == "resources/list":
        return JSONResponse(_rpc_result(req_id, {"resources": APP_RESOURCES}))
    if method == "resources/read":
        params = msg.get("params") or {}
        if params.get("uri") != REPAIR_CARD_RESOURCE_URI:
            return JSONResponse(_rpc_error(req_id, -32002, "Resource not found"))
        return JSONResponse(_rpc_result(req_id, {"contents": [repair_card_resource_contents()]}))
    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            if name == "record_change": payload = sess.record_change(str(args["utterance"]))
            elif name == "preview_repair_plan": payload = sess.preview()
            elif name == "approve_repair_plan": payload = sess.approve(args)
            elif name == "execute_repair_plan": payload = sess.execute()
            elif name == "get_repair_status": payload = sess.status()
            else: return JSONResponse(_rpc_error(req_id, -32602, f"Unknown tool: {name}"))
            return JSONResponse(_rpc_result(
                req_id,
                _tool_result(
                    payload,
                    ui_resource_uri=REPAIR_CARD_RESOURCE_URI if name == "preview_repair_plan" else None,
                ),
            ))
        except (KeyError, TypeError, ValueError) as exc:
            return JSONResponse(_rpc_result(req_id, _tool_result({"error": str(exc)}, is_error=True)))
    return JSONResponse(_rpc_error(req_id, -32601, "Method not found"))


async def mcp_get(request: Request) -> Response:
    if not _valid_origin(request):
        return JSONResponse(_rpc_error(None, -32000, "Invalid Origin"), status_code=403)
    if _authenticate_any(request, ("mcp:service", "mcp:tools")) is None:
        return _unauthorized(None)
    return Response(status_code=405, headers={"Allow": "POST, GET, DELETE"})


async def mcp_delete(request: Request) -> Response:
    if not _valid_origin(request):
        return JSONResponse(_rpc_error(None, -32000, "Invalid Origin"), status_code=403)
    if _authenticate_any(request, ("mcp:service", "mcp:tools")) is None:
        return _unauthorized(None)
    _cleanup_sessions()
    sid = request.headers.get("mcp-session-id")
    if not sid or sid not in SESSIONS:
        return Response(status_code=404)
    del SESSIONS[sid]
    return Response(status_code=204)


async def healthz(request: Request) -> Response:
    return JSONResponse({"status": "ok", "service": SERVER_INFO["name"], "version": SERVER_INFO["version"], "protocol": PROTOCOL_VERSION})


async def readyz(request: Request) -> Response:
    try:
        c = load_auth_config()
        return JSONResponse({"status": "ready", "resource": c.resource, "environment": c.environment})
    except Exception as exc:
        return JSONResponse({"status": "not_ready", "error": str(exc)}, status_code=503)


async def root(request: Request) -> Response:
    return JSONResponse({"service": SERVER_INFO, "mcp_endpoint": "/mcp", "health": "/healthz"})


app = Starlette(routes=[
    Route("/", root, methods=["GET"]),
    Route("/healthz", healthz, methods=["GET"]),
    Route("/readyz", readyz, methods=["GET"]),
    Route("/.well-known/oauth-protected-resource", protected_resource_metadata, methods=["GET"]),
    Route("/.well-known/oauth-authorization-server", authorization_server_metadata, methods=["GET"]),
    Route("/oauth/authorize", authorize, methods=["GET", "POST"]),
    Route("/oauth/token", token, methods=["POST"]),
    Route("/mcp", mcp_post, methods=["POST"]),
    Route("/mcp", mcp_get, methods=["GET"]),
    Route("/mcp", mcp_delete, methods=["DELETE"]),
])


def serve(host: str | None = None, port: int | None = None) -> None:
    import uvicorn
    bind_host = host or os.getenv("RIPPLE_HOST", "0.0.0.0")
    bind_port = port or int(os.getenv("PORT", os.getenv("RIPPLE_PORT", "8000")))
    uvicorn.run(app, host=bind_host, port=bind_port, proxy_headers=True, forwarded_allow_ips="*")


if __name__ == "__main__":
    serve()
