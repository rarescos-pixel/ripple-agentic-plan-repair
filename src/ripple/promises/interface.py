"""Opt-in MCP tools, with human authority on a separate authenticated route."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import hmac
import json
import os
from pathlib import Path
import secrets
from urllib.parse import quote

from starlette.responses import JSONResponse
from starlette.routing import Route

from .engine import PromiseEngine
from .interpreter import BedrockIntentInterpreter
from .provider_http import HttpWorld
from .store import build_promise_store
from .worker import PromiseWorker


def enabled(): return os.getenv("RIPPLE_PROMISES_ENABLED", "false").lower() == "true"


def promise_tools():
    definitions = [
        ("draft_promise_intent", "Draft an Intent Contract from human intent for separate meaning confirmation. Never activates or authorizes effects.", {"utterance": {"type": "string", "maxLength": 2000}}, ["utterance"], False),
        ("clarify_promise_intent", "Apply a human clarification to a DRAFT contract. Returns a new version for meaning confirmation. Cannot change an active contract.", {"contract_id": {"type": "string"}, "utterance": {"type": "string", "maxLength": 2000}}, ["contract_id", "utterance"], False),
        ("get_promise", "Read a promise, its current plan and verified evidence across sessions.", {"contract_id": {"type": "string"}}, ["contract_id"], True),
        ("reconcile_promise", "Observe trusted provider state and project the current plan forward. Propose minimal repair; no external writes.", {"contract_id": {"type": "string"}}, ["contract_id"], False),
        ("execute_promise", "Execute only a due delta inside existing confirmed and exact approved authority, then independently verify. Never creates authority.", {"contract_id": {"type": "string"}}, ["contract_id"], False),
    ]
    return [{"name": name, "description": description, "inputSchema": {"type": "object", "properties": properties, "required": required, "additionalProperties": False},
             "annotations": {"readOnlyHint": readonly, "destructiveHint": name == "execute_promise", "idempotentHint": name != "draft_promise_intent", "openWorldHint": False}}
            for name, description, properties, required, readonly in definitions]


class PromiseService:
    def __init__(self, engine, interpreter, owner, human_token):
        if not owner or not isinstance(human_token, str) or len(human_token) < 32:
            raise ValueError("Explicit promise owner and independent human credential required")
        self.engine, self.interpreter, self.owner, self.human_token = engine, interpreter, owner, human_token
        self.worker = PromiseWorker(engine)

    @staticmethod
    def present(state):
        """Bound conversational output; detailed proof stays in the human ledger."""
        return {k: state[k] for k in ("id", "phase", "decision", "reason", "contract", "contract_version", "contract_hash",
                "world_version", "plan_version", "plan", "binding", "assumptions", "threat")} | {
            "verified_effects": sum(r["verified"] for r in state["receipts"]),
            "last_receipt": ({"key": state["receipts"][-1]["key"], "verified": state["receipts"][-1]["verified"]} if state["receipts"] else None),
            "authority_note": "Meaning confirmation and consequential approval require the separate authenticated human review surface.",
            "human_review_url": os.getenv("RIPPLE_PUBLIC_BASE_URL", "").rstrip("/") + "/promises/review/" + quote(state["id"], safe=""),
            "execution_conditions": state["execution_conditions"],
        }

    def call(self, name, arguments, owner):
        if owner != self.owner: raise ValueError("Promise environment not available for this principal")
        definitions = {x["name"]: x for x in promise_tools()}
        if name not in definitions: raise ValueError("Unknown promise tool; human authority is not a model tool")
        expected = set(definitions[name]["inputSchema"]["required"])
        if not isinstance(arguments, dict) or set(arguments) != expected or any(not isinstance(v, str) or not v for v in arguments.values()):
            raise ValueError("Exact promise tool arguments required")
        if name == "draft_promise_intent":
            world = self.engine.provider.read()
            context = {"world": world["facts"], "catalog": self.engine.catalog, "source": world["source"],
                       "now": self.engine.clock(), "time_zone": os.getenv("RIPPLE_PROMISE_TIME_ZONE", "UTC")}
            spec = self.interpreter.interpret(arguments["utterance"], context)
            contract_id = "promise-" + secrets.token_hex(12)
            # Register before creating: a crash can leave an inert missing ID,
            # but never an ACTIVE contract omitted from observation.
            self.worker.register(contract_id)
            return self.engine.draft(contract_id, owner, spec)
        contract_id = arguments["contract_id"]
        existing = self.engine.get(contract_id, owner)  # ownership before any observation/effect
        if name == "clarify_promise_intent":
            if existing["phase"] != "DRAFT": raise ValueError("A model cannot revise an active confirmed contract")
            world = self.engine.provider.read()
            spec = self.interpreter.interpret(arguments["utterance"], {"world": world["facts"], "catalog": self.engine.catalog,
                "source": world["source"], "now": self.engine.clock(), "previous_draft": existing["contract"],
                "time_zone": os.getenv("RIPPLE_PROMISE_TIME_ZONE", "UTC")})
            return self.engine.revise(contract_id, owner, spec)
        if name == "get_promise": return self.engine.get(contract_id, owner)
        if name == "reconcile_promise": return self.engine.reconcile(contract_id)
        return self.engine.execute(contract_id)


def build_service():
    from ripple.aws.bedrock import TrackedBedrockConverseClient
    from ripple.aws.runtime import build_trace_sink
    catalog = json.loads(Path(os.environ["RIPPLE_PROMISE_CATALOG_PATH"]).read_text())
    human_token = os.environ["RIPPLE_PROMISE_HUMAN_TOKEN"]
    provider_token = os.environ["RIPPLE_PROMISE_PROVIDER_TOKEN"]
    if human_token in {provider_token, os.getenv("RIPPLE_SERVICE_CLIENT_SECRET"), os.getenv("RIPPLE_DEMO_USER_PASSWORD")}:
        raise ValueError("Human authority credential must be separate from MCP and provider credentials")
    provider = HttpWorld(os.environ["RIPPLE_PROMISE_PROVIDER_URL"], provider_token)
    engine = PromiseEngine(build_promise_store(), provider, catalog, trace=build_trace_sink())
    interpreter = BedrockIntentInterpreter(TrackedBedrockConverseClient(region_name=os.getenv("AWS_REGION", "eu-central-1")), os.environ["RIPPLE_BEDROCK_MODEL_ID"])
    return PromiseService(engine, interpreter, os.environ["RIPPLE_PROMISE_OWNER"], human_token)


def get_service(request):
    if not enabled(): raise ValueError("Continuous promises are not enabled")
    service = getattr(request.app.state, "promise_service", None)
    if service is None:
        service = build_service()
        request.app.state.promise_service = service
    return service


def human_routes(service_factory=get_service):
    async def endpoint(request):
        try: service = service_factory(request)
        except (ValueError, KeyError, RuntimeError): return JSONResponse({"error": "Promise interface unavailable"}, status_code=404)
        if not hmac.compare_digest(request.headers.get("authorization", ""), "Bearer " + service.human_token):
            return JSONResponse({"error": "Independent human authorization required"}, status_code=401)
        headers = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}
        try:
            contract_id, operation = request.path_params["contract_id"], request.path_params["operation"]
            if request.method == "GET" and operation == "review":
                state = await asyncio.to_thread(service.engine.get, contract_id, service.owner)
            elif request.method == "POST":
                raw = await request.body()
                if len(raw) > 24000: raise ValueError("Human request exceeds bounded schema")
                args = json.loads(raw)
                if operation == "confirm" and set(args) == {"contract_version", "contract_hash"}:
                    state = await asyncio.to_thread(service.engine.confirm, contract_id, service.owner, args["contract_version"], args["contract_hash"])
                elif operation == "approve" and set(args) == {"binding"}:
                    state = await asyncio.to_thread(service.engine.approve, contract_id, service.owner, args["binding"])
                elif operation == "revise" and set(args) == {"contract"}:
                    state = await asyncio.to_thread(service.engine.revise, contract_id, service.owner, args["contract"])
                elif operation == "revoke" and args == {}:
                    state = await asyncio.to_thread(service.engine.revoke, contract_id, service.owner)
                else: raise ValueError("Unknown human operation or unexpected fields")
            else: raise ValueError("Unknown human operation")
            return JSONResponse(state, headers=headers)
        except (ValueError, KeyError, TypeError) as exc:
            return JSONResponse({"error": str(exc)}, status_code=409, headers=headers)
    from .review import review_page
    return [Route("/promises/human/{contract_id}/{operation}", endpoint, methods=["GET", "POST"]),
            Route("/promises/review/{contract_id}", review_page, methods=["GET"])]


@asynccontextmanager
async def promise_lifespan(app):
    task = None
    if enabled():
        service = getattr(app.state, "promise_service", None) or build_service()
        app.state.promise_service = service
        interval = float(os.getenv("RIPPLE_PROMISE_POLL_SECONDS", "5"))
        if not 1 <= interval <= 60: raise ValueError("Promise polling interval must be 1..60 seconds")
        async def watch():
            while True:
                await asyncio.to_thread(service.worker.tick)
                await asyncio.sleep(interval)
        task = asyncio.create_task(watch())
    try: yield
    finally:
        if task:
            task.cancel()
            try: await task
            except asyncio.CancelledError: pass
