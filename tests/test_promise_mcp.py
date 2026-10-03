import asyncio
from copy import deepcopy

from test_mcp_app_repair_card import reset, client, user_token, initialize, headers, rpc
from test_promise_acceptance import setup_engine
from test_promise_interface import DraftModel, HUMAN_KEY
from ripple.mcp_server import app
from ripple.promises.interface import PromiseService
from ripple.promises.interpreter import BedrockIntentInterpreter


def test_opt_in_mcp_continuity_and_no_model_approval_tools(tmp_path, monkeypatch):
    e, p, c, s = setup_engine(tmp_path)
    service = PromiseService(e, BedrockIntentInterpreter(DraftModel(s["contract"]), "test-model"), "demo-user", HUMAN_KEY)
    monkeypatch.setenv("RIPPLE_PROMISES_ENABLED", "true")
    monkeypatch.setattr(app.state, "promise_service", service, raising=False)
    async def scenario():
        reset()
        async with await client() as http:
            token = await user_token(http)
            sid = await initialize(http, token)
            h = headers(token, sid)
            listed = await rpc(http, h, 11, "tools/list")
            names = {x["name"] for x in listed.json()["result"]["tools"]}
            assert names == {"draft_promise_intent", "clarify_promise_intent", "get_promise", "reconcile_promise", "execute_promise"}
            legacy_approval = await rpc(http, h, 111, "tools/call", {"name": "approve_repair_plan", "arguments": {"user_confirmed": True}})
            assert legacy_approval.json()["error"]["code"] == -32602
            drafted = await rpc(http, h, 12, "tools/call", {"name": "draft_promise_intent", "arguments": {"utterance": "Keep delivery ready while staying within budget."}})
            state = drafted.json()["result"]["structuredContent"]
            assert state["phase"] == "DRAFT" and p.write_count() == 0
            contract_id = state["id"]
            assert state["human_review_url"].endswith("/promises/review/" + contract_id)
            assert (await http.post(f"/promises/human/{contract_id}/confirm", headers={"Authorization": f"Bearer {token}"}, json={"contract_version": 1, "contract_hash": state["contract_hash"]})).status_code == 401
            human = {"Authorization": f"Bearer {HUMAN_KEY}"}
            assert (await http.post(f"/promises/human/{contract_id}/confirm", headers=human, json={"contract_version": 1, "contract_hash": state["contract_hash"]})).status_code == 200
            # A new MCP session reads the same durable contract.
            sid2 = await initialize(http, token)
            r = await rpc(http, headers(token, sid2), 13, "tools/call", {"name": "reconcile_promise", "arguments": {"contract_id": contract_id}})
            active = r.json()["result"]["structuredContent"]
            assert active["contract_version"] == 1 and active["decision"] == "REQUEST_APPROVAL"
            assert p.write_count() == 0
    asyncio.run(scenario())
