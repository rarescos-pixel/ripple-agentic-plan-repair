import asyncio

from test_mcp_app_repair_card import reset, client, user_token, initialize, headers, rpc
from test_promise_acceptance import setup_engine
from test_promise_interface import DraftModel, HUMAN_KEY
from ripple.mcp_server import app
from ripple.promises.interface import PromiseService
from ripple.promises.interpreter import BedrockIntentInterpreter


def test_rules_permitted_alexa_simulation_runs_promise_mode_end_to_end(tmp_path, monkeypatch):
    """Exercise the hackathon-permitted Alexa+ simulation through the real MCP surface.

    The simulated host may discover and invoke MCP tools, but it cannot mint either
    human meaning confirmation or exact action approval. Those authority events use
    the separate authenticated human route. A fresh MCP session is used between
    every consequential phase to prove that conversational session identity is not
    the persistence boundary.
    """
    engine, provider, clock, scenario = setup_engine(tmp_path)
    service = PromiseService(
        engine,
        BedrockIntentInterpreter(DraftModel(scenario["contract"]), "test-model"),
        "demo-user",
        HUMAN_KEY,
    )
    monkeypatch.setenv("RIPPLE_PROMISES_ENABLED", "true")
    monkeypatch.setattr(app.state, "promise_service", service, raising=False)

    async def scenario_run():
        reset()
        async with await client() as http:
            token = await user_token(http)

            # Turn/session 1: Alexa+ host discovers the promise tool surface.
            sid1 = await initialize(http, token)
            listed = await rpc(http, headers(token, sid1), 1, "tools/list")
            names = {tool["name"] for tool in listed.json()["result"]["tools"]}
            assert names == {
                "draft_promise_intent",
                "clarify_promise_intent",
                "get_promise",
                "reconcile_promise",
                "execute_promise",
            }
            assert not any("approv" in name or "confirm" in name for name in names)

            drafted_response = await rpc(
                http,
                headers(token, sid1),
                2,
                "tools/call",
                {
                    "name": "draft_promise_intent",
                    "arguments": {
                        "utterance": "Keep the delivery ready while staying within budget."
                    },
                },
            )
            drafted = drafted_response.json()["result"]["structuredContent"]
            assert drafted["phase"] == "DRAFT"
            assert provider.write_count() == 0
            contract_id = drafted["id"]

            # Meaning confirmation is human authority, not an MCP/model tool.
            human = {"Authorization": f"Bearer {HUMAN_KEY}"}
            confirmed = await http.post(
                f"/promises/human/{contract_id}/confirm",
                headers=human,
                json={
                    "contract_version": drafted["contract_version"],
                    "contract_hash": drafted["contract_hash"],
                },
            )
            assert confirmed.status_code == 200
            assert provider.write_count() == 0

            # Turn/session 2: a new Alexa conversation/session reconstructs the
            # durable promise and observes that an exact action binding needs approval.
            sid2 = await initialize(http, token)
            reconciled_response = await rpc(
                http,
                headers(token, sid2),
                3,
                "tools/call",
                {"name": "reconcile_promise", "arguments": {"contract_id": contract_id}},
            )
            reconciled = reconciled_response.json()["result"]["structuredContent"]
            assert reconciled["id"] == contract_id
            assert reconciled["decision"] == "REQUEST_APPROVAL"
            assert reconciled["binding"]
            assert provider.write_count() == 0

            # Calling the model-visible execution tool before independent human
            # approval must still produce zero provider writes.
            await rpc(
                http,
                headers(token, sid2),
                4,
                "tools/call",
                {"name": "execute_promise", "arguments": {"contract_id": contract_id}},
            )
            assert provider.write_count() == 0

            # Exact action approval is a second, distinct human authority event.
            approved = await http.post(
                f"/promises/human/{contract_id}/approve",
                headers=human,
                json={"binding": reconciled["binding"]},
            )
            assert approved.status_code == 200
            assert provider.write_count() == 0

            # Make the approved delta due, then execute it from yet another MCP session.
            clock.value = 100
            sid3 = await initialize(http, token)
            executed_response = await rpc(
                http,
                headers(token, sid3),
                5,
                "tools/call",
                {"name": "execute_promise", "arguments": {"contract_id": contract_id}},
            )
            executed = executed_response.json()["result"]["structuredContent"]
            assert executed["id"] == contract_id
            assert provider.write_count() == 1
            assert executed["verified_effects"] >= 1
            assert executed["last_receipt"] and executed["last_receipt"]["verified"] is True

            # Turn/session 4: continuity survives MCP session replacement and the
            # verified result remains readable without replaying the physical effect.
            sid4 = await initialize(http, token)
            readback_response = await rpc(
                http,
                headers(token, sid4),
                6,
                "tools/call",
                {"name": "get_promise", "arguments": {"contract_id": contract_id}},
            )
            readback = readback_response.json()["result"]["structuredContent"]
            assert readback["id"] == contract_id
            assert readback["verified_effects"] >= 1
            assert readback["last_receipt"] and readback["last_receipt"]["verified"] is True
            assert provider.write_count() == 1

    asyncio.run(scenario_run())
