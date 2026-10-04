from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import pytest

from test_promise_acceptance import setup_engine, activate, approve, eq
from ripple.promises.engine import PromiseEngine
from ripple.promises.model import digest, evaluate, validate_expr
from ripple.promises.planner import plan
from ripple.promises.provider import SqliteWorld
from ripple.promises.store import Conflict, DynamoPromiseStore, SqlitePromiseStore


def test_crash_after_provider_commit_recovers_without_duplicate(tmp_path):
    class CrashOnce(SqliteWorld):
        crashed = False
        def apply(self, *args):
            result = super().apply(*args)
            if not self.crashed:
                self.crashed = True
                raise SystemExit("power loss after provider effect, before receipt")
            return result
    e, p, c, s = setup_engine(tmp_path, provider_class=CrashOnce)
    activate(e, s)
    approve(e)
    c.value = 100
    with pytest.raises(SystemExit): e.execute("p")
    assert p.write_count() == 1 and e.get("p", "owner")["pending"]
    restarted = PromiseEngine(SqlitePromiseStore(tmp_path / "promises.db"), p, e.catalog, clock=c)
    s = restarted.execute("p")
    assert p.write_count() == 1 and len(s["receipts"]) == 1
    assert s["receipts"][0]["verified"] and s["pending"] is None


def test_concurrent_workers_cannot_create_duplicate_effects(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    approve(e)
    c.value = 100
    def run(_):
        engine = PromiseEngine(SqlitePromiseStore(tmp_path / "promises.db"), p, e.catalog, clock=c)
        try: return engine.execute("p")
        except Conflict: return "CAS conflict, reload"
    with ThreadPoolExecutor(max_workers=4) as pool: list(pool.map(run, range(8)))
    assert p.write_count() == 1
    assert len(e.get("p", "owner")["receipts"]) == 1


def test_world_changes_between_reservation_and_provider_commit(tmp_path):
    class Race(SqliteWorld):
        def apply(self, *args):
            self.change({"available": False})
            return super().apply(*args)
    e, p, c, s = setup_engine(tmp_path, provider_class=Race)
    activate(e, s)
    approve(e)
    c.value = 100
    e.execute("p")
    assert p.write_count() == 0
    assert e.reconcile("p")["phase"] == "UNSATISFIABLE"


def test_conditional_expiry_during_network_wait_blocks_commit(tmp_path):
    class Delay(SqliteWorld):
        def apply(self, *args):
            self.clock.value = 101
            return super().apply(*args)
    e, p, c, s = setup_engine(tmp_path, provider_class=Delay,
        spec_edit=lambda x: x["expiry"].update(when={"ge": [{"fact": "$now"}, {"literal": 101}]}))
    activate(e, s)
    approve(e)
    c.value = 100
    e.execute("p")
    assert p.write_count() == 0
    assert e.reconcile("p")["phase"] == "EXPIRED"


def test_invariant_time_boundary_during_network_wait_blocks_commit(tmp_path):
    class Delay(SqliteWorld):
        def apply(self, *args):
            self.clock.value = 101
            return super().apply(*args)
    def edit(x):
        x["invariants"].append({"id": "window", "predicate": {"implies": [eq("delivery_route", "ready"),
            {"le": [{"fact": "$now"}, {"literal": 100}]}]}})
    e, p, c, s = setup_engine(tmp_path, provider_class=Delay, spec_edit=edit)
    activate(e, s)
    approve(e)
    c.value = 100
    e.execute("p")
    assert p.write_count() == 0


def test_unknown_fact_and_bool_number_confusion_do_not_authorize(tmp_path):
    assert evaluate(eq("x", 1), {"x": True}, 0) is None
    assert evaluate(eq("x", True), {}, 0) is None
    with pytest.raises(ValueError): validate_expr({"python": "__import__('os')"})
    with pytest.raises(ValueError): validate_expr({"and": []})
    e, p, c, s = setup_engine(tmp_path)
    p.change({"budget_ok": 1})
    assert activate(e, s)["decision"] == "REQUEST_CLARIFICATION"
    assert p.write_count() == 0


def test_search_limit_is_not_impossibility(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    e.max_candidates = 1
    s = activate(e, s)
    assert s["decision"] == "REQUEST_CLARIFICATION" and s["phase"] != "UNSATISFIABLE"


def test_minimal_edit_candidate_is_unsafe_so_safe_larger_repair_wins(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    spec = deepcopy(s["contract"])
    spec["goal"] = {"or": [eq("delivery_route", "ready"), eq("fallback", "ready")]}
    spec["authority"]["fallback"] = "APPROVAL_REQUIRED"
    catalog = {**e.catalog, "fallback": {"values": ["waiting", "ready"], "times": ["now"], "reversible": True}}
    facts = {**p.read()["facts"], "fallback": "waiting", "available": False}
    previous = [{"at": 10, "writes": {"delivery_route": "ready"}}]
    result = plan(spec, facts, catalog, previous, 10)
    assert result["actions"] == [{"at": 10, "writes": {"fallback": "ready"}}]
    assert result["evaluation"]["valid"]


def test_reversible_authority_must_be_confirmed_and_deployment_allowed(tmp_path):
    e, p, c, s = setup_engine(tmp_path, spec_edit=lambda x: x["authority"].update(delivery_route="AUTONOMOUS_REVERSIBLE"))
    assert e.execute("p")["phase"] == "DRAFT" and p.write_count() == 0
    activate(e, s)
    c.value = 100
    s = e.execute("p")
    assert s["receipts"][0]["approval_mode"] == "confirmed_reversible_envelope"
    assert p.write_count() == 1


def test_expiry_revocation_and_catalog_drift_are_fail_closed(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    approve(e)
    e.revoke("p", "owner")
    c.value = 100
    assert e.execute("p")["phase"] == "REVOKED" and p.write_count() == 0
    catalog = deepcopy(e.catalog)
    catalog["delivery_route"]["values"].append("unsafe")
    e2 = PromiseEngine(e.store, p, catalog, clock=c)
    with pytest.raises(ValueError, match="catalogue"): e2.execute("p")


def test_capacity_failure_happens_before_effect(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    approve(e)
    s = e.get("p", "owner")
    for _ in range(241 - len(s["ledger"])): e._log(s, "test.capacity")
    e._save(s)
    c.value = 100
    with pytest.raises(ValueError, match="capacity"): e.execute("p")
    assert p.write_count() == 0


def test_ledger_content_can_be_verified(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    approve(e)
    c.value = 100
    s = e.execute("p")
    previous = None
    for row in s["ledger"]:
        assert row["previous"] == previous
        assert row["hash"] == digest({k: v for k, v in row.items() if k != "hash"})
        previous = row["hash"]


def test_dynamo_store_uses_existing_permissions_and_atomic_revision():
    class Conditional(Exception):
        response = {"Error": {"Code": "ConditionalCheckFailedException"}}
    class Client:
        item = None
        def get_item(self, **kwargs):
            assert kwargs["ConsistentRead"] is True
            return {"Item": self.item} if self.item else {}
        def put_item(self, **kwargs):
            if "ExpressionAttributeValues" in kwargs:
                if not self.item or self.item["revision"] != kwargs["ExpressionAttributeValues"][":old"]: raise Conditional()
            elif self.item: raise Conditional()
            self.item = deepcopy(kwargs["Item"])
    client = Client()
    store = DynamoPromiseStore("existing-table", client)
    store.save({"id": "p", "revision": 1}, 0)
    with pytest.raises(Conflict): store.save({"id": "p", "revision": 1}, 0)
    store.save({"id": "p", "revision": 2}, 1)
    with pytest.raises(Conflict): store.save({"id": "p", "revision": 3}, 1)
    assert store.load("p")["revision"] == 2


def test_late_unfulfilled_goal_is_not_silently_moved(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    approve(e)
    c.value = 101
    s = e.execute("p")
    assert s["phase"] == "UNSATISFIABLE"
    assert p.write_count() == 0


def test_achieved_goal_remains_under_reconciliation_until_completion(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    approve(e)
    c.value = 100
    e.execute("p")
    c.value = 110
    p.change({"delivery_route": "waiting"})
    s = e.reconcile("p")
    assert s["decision"] == "REQUEST_APPROVAL" and s["phase"] == "ACTIVE"
    assert s["goal_evidence"]["verified_at"] == 100
    approve(e)
    s = e.execute("p")
    assert p.write_count() == 2 and s["receipts"][-1]["verified"]


def test_observe_immediately_invalidates_old_binding(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    binding = approve(e)
    p.change({"deadline": 120})
    e.observe("p", p.read())
    with pytest.raises(ValueError, match="stale"): e.approve("p", "owner", binding)
    assert p.write_count() == 0


def test_late_missing_goal_evidence_is_not_unsatisfiable_or_satisfied(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    c.value = 110
    p.change({"delivery_route": None})
    state = e.reconcile("p")
    assert state["decision"] == "REQUEST_CLARIFICATION"
    assert state["phase"] not in {"UNSATISFIABLE", "SATISFIED"}


def test_external_completion_removes_obsolete_effect_instead_of_repeating_it(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    approve(e)
    p.change({"delivery_route": "ready"})
    state = e.reconcile("p")
    assert state["plan"]["actions"] == [] and state["decision"] == "WAIT"
    c.value = 100
    e.execute("p")
    assert p.write_count() == 0


def test_unconfirmed_contract_expires_without_becoming_an_eternal_draft(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    c.value = 201
    assert e.reconcile("p")["phase"] == "EXPIRED"
    assert p.write_count() == 0
    with pytest.raises(ValueError): e.confirm("p", "owner", 1, s["contract_hash"])
