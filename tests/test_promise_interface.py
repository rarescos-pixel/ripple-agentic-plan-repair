from copy import deepcopy
import json
import pytest
from starlette.testclient import TestClient

from test_promise_acceptance import setup_engine, activate, approve
from ripple.promises.interpreter import BedrockIntentInterpreter
from ripple.promises.interface import PromiseService, human_routes, promise_tools
from ripple.promises.worker import PromiseWorker
from ripple.promises.provider_http import HttpWorld, provider_app
from starlette.applications import Starlette


HUMAN_KEY = "human-only-review-key-" + "x" * 32
PROVIDER_KEY = "provider-only-write-key-" + "y" * 32


def contract_wire(spec, confidence=.99):
    """Deterministically encode canonical test fixtures into the untrusted wire format."""
    nodes = []
    counter = 0

    def add(expr):
        nonlocal counter
        counter += 1
        node_id = f"n{counter}"
        op, value = next(iter(expr.items()))
        if op == "fact":
            nodes.append({"id": node_id, "kind": "fact", "fact": value})
        elif op == "literal":
            if isinstance(value, bool): literal_type, literal_value = "boolean", "true" if value else "false"
            elif value is None: literal_type, literal_value = "null", "null"
            elif type(value) is int: literal_type, literal_value = "integer", str(value)
            elif type(value) is float: literal_type, literal_value = "number", json.dumps(value, allow_nan=False)
            elif isinstance(value, str): literal_type, literal_value = "string", value
            else: raise ValueError("Unsupported fixture literal")
            nodes.append({"id": node_id, "kind": "literal", "literal_type": literal_type, "literal_value": literal_value})
        else:
            children = [add(child) for child in value]
            nodes.append({"id": node_id, "kind": "operator", "operator": op, "args": children})
        return node_id

    def rows(items):
        result = []
        for item in items:
            row = {"id": item["id"], "root": add(item["predicate"])}
            if "label" in item: row["label"] = item["label"]
            result.append(row)
        return result

    data = {
        "goal_root": add(spec["goal"]),
        "goal_at_root": add(spec["goal_at"]),
        "invariants": rows(spec["invariants"]),
        "assumptions": rows(spec["assumptions"]),
        "authority": [{"name": name, "permission": permission} for name, permission in spec["authority"].items()],
        "expiry_at": spec["expiry"]["at"],
        "evidence_source": spec["evidence"]["source"],
        "evidence_max_age_seconds": spec["evidence"]["max_age_seconds"],
        "completion_root": add(spec["completion"]),
        "meaning": spec["meaning"],
        "questions": list(spec["questions"]),
        "confidence": confidence,
    }
    if "when" in spec["expiry"]: data["expiry_when_root"] = add(spec["expiry"]["when"])
    data["nodes"] = nodes
    return data


class DraftModel:
    def __init__(self, spec): self.spec = spec
    def converse(self, **kwargs):
        self.request = kwargs
        return {"stopReason": "tool_use", "output": {"message": {"content": [{"toolUse": {"name": "draft_intent_contract", "input": contract_wire(self.spec)}}]}}}


def test_bedrock_only_drafts_and_rejects_invented_facts_and_low_confidence(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    model = DraftModel(s["contract"])
    interpreter = BedrockIntentInterpreter(model, "test-model")
    spec = interpreter.interpret("Keep the promise", {"world": p.read()["facts"], "catalog": e.catalog, "now": c(), "source": "test-world"})
    assert spec == s["contract"] and p.write_count() == 0
    assert model.request["toolConfig"]["toolChoice"] == {"tool": {"name": "draft_intent_contract"}}
    model.spec["goal"] = {"eq": [{"fact": "invented"}, {"literal": True}]}
    with pytest.raises(ValueError, match="fact"): interpreter.interpret("x", {"world": p.read()["facts"], "catalog": e.catalog, "now": c(), "source": "test-world"})


def test_mcp_cannot_mint_human_confirmation_or_action_approval(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    service = PromiseService(e, BedrockIntentInterpreter(DraftModel(s["contract"]), "test-model"), "owner", HUMAN_KEY)
    names = {x["name"] for x in promise_tools()}
    assert not any("approv" in n or "confirm" in n for n in names)
    app = Starlette(routes=human_routes(lambda request: service))
    with TestClient(app) as client:
        url = "/promises/human/p/confirm"
        body = {"contract_version": 1, "contract_hash": s["contract_hash"]}
        assert client.post(url, json=body, headers={"Authorization": "Bearer arbitrary-mcp-user-token"}).status_code == 401
        assert p.write_count() == 0
        headers = {"Authorization": f"Bearer {HUMAN_KEY}"}
        assert client.post(url, json=body, headers=headers).status_code == 200
        s = service.call("reconcile_promise", {"contract_id": "p"}, "owner")
        assert s["decision"] == "REQUEST_APPROVAL"
        service.call("execute_promise", {"contract_id": "p"}, "owner")
        assert p.write_count() == 0
        with pytest.raises(ValueError): service.call("approve_promise", {}, "owner")
        assert client.post("/promises/human/p/approve", json={"binding": s["binding"]}, headers=headers).status_code == 200
        c.value = 100
        service.call("execute_promise", {"contract_id": "p"}, "owner")
        assert p.write_count() == 1
        with pytest.raises(ValueError): service.call("get_promise", {"contract_id": "p", "owner": "other"}, "other")


def test_worker_watchlist_survives_restart_and_observes_without_new_user_command(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    worker = PromiseWorker(e)
    worker.register("p")
    approve(e)
    p.change({"available": False})
    restarted = PromiseWorker(e)
    result = restarted.tick()["p"]
    assert result["phase"] == "UNSATISFIABLE"
    assert e.get("p", "owner")["threat"]
    assert p.write_count() == 0


def test_http_provider_requires_own_credential_and_preserves_readback(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    with TestClient(provider_app(p, PROVIDER_KEY)) as client:
        assert client.get("/world").status_code == 401
        provider = HttpWorld("http://127.0.0.1", PROVIDER_KEY, client=client)
        e.provider = provider
        activate(e, s)
        approve(e)
        c.value = 100
        s = e.execute("p")
        assert s["receipts"][0]["verified"]
        assert provider.read()["facts"]["delivery_route"] == "ready"
        assert p.write_count() == 1


def test_clarification_revises_only_unconfirmed_meaning(tmp_path):
    e, p, c, s = setup_engine(tmp_path, spec_edit=lambda x: x.update(questions=["Which outcome?"]))
    corrected = deepcopy(s["contract"])
    corrected["questions"] = []
    corrected["meaning"] = "Corrected meaning from the human reply"
    service = PromiseService(e, BedrockIntentInterpreter(DraftModel(corrected), "test-model"), "owner", HUMAN_KEY)
    state = service.call("clarify_promise_intent", {"contract_id": "p", "utterance": "Use the original route within budget"}, "owner")
    assert state["contract_version"] == 2 and state["phase"] == "DRAFT" and p.write_count() == 0
    with pytest.raises(ValueError): e.confirm("p", "owner", 1, s["contract_hash"])
    e.confirm("p", "owner", 2, state["contract_hash"])
    with pytest.raises(ValueError, match="active"): service.call("clarify_promise_intent", {"contract_id": "p", "utterance": "Ignore the budget"}, "owner")


def test_low_confidence_draft_cannot_be_silently_activated(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    class Uncertain(DraftModel):
        def converse(self, **kwargs):
            response = super().converse(**kwargs)
            response["output"]["message"]["content"][0]["toolUse"]["input"]["confidence"] = .2
            return response
    service = PromiseService(e, BedrockIntentInterpreter(Uncertain(s["contract"]), "test-model"), "owner", HUMAN_KEY)
    draft = service.call("draft_promise_intent", {"utterance": "Keep it okay"}, "owner")
    assert draft["contract"]["questions"]
    with pytest.raises(ValueError, match="clarification"): e.confirm(draft["id"], "owner", 1, draft["contract_hash"])
    assert p.write_count() == 0


def test_human_review_page_contains_no_contract_or_credential_before_auth(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    service = PromiseService(e, None, "owner", HUMAN_KEY)
    with TestClient(Starlette(routes=human_routes(lambda request: service))) as client:
        response = client.get("/promises/review/p")
        assert response.status_code == 200
        assert HUMAN_KEY not in response.text and s["contract"]["meaning"] not in response.text
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
        assert client.get("/promises/human/p/review").status_code == 401
