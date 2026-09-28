"""Behavioral first gate. Each test is a claim about effects, not code shape."""
from copy import deepcopy
import pytest

from ripple.promises.engine import PromiseEngine
from ripple.promises.model import digest
from ripple.promises.provider import SqliteWorld
from ripple.promises.store import SqlitePromiseStore


def eq(key, value):
    return {"eq": [{"fact": key}, {"literal": value}]}


def fixture_spec(domain="business"):
    # Identical engine and operator set, different facts/tools/evidence.
    target, constraint = {
        "business": ("delivery_route", "budget_ok"),
        "software": ("release_channel", "security_approved"),
        "household": ("entry_mode", "occupant_access"),
    }[domain]
    return {
        "goal": eq(target, "ready"), "goal_at": {"fact": "deadline"},
        "invariants": [{"id": "protected", "label": constraint, "predicate": eq(constraint, True)},
                       {"id": "route_available", "label": "Selected route remains available",
                        "predicate": {"implies": [eq(target, "ready"), eq("available", True)]}}],
        "assumptions": [{"id": "availability", "predicate": eq("available", True)}],
        "authority": {target: "APPROVAL_REQUIRED", constraint: "FORBIDDEN"},
        "expiry": {"at": 200}, "completion": eq("finished", True),
        "evidence": {"source": "test-world", "max_age_seconds": 100},
        "meaning": "Make ready while preserving the constraint; ask before writes.",
        "questions": [],
    }, {target: {"values": ["waiting", "ready"], "times": ["now", "goal"], "reversible": True}}


class Clock:
    def __init__(self): self.value = 10
    def __call__(self): return self.value


def setup_engine(tmp_path, domain="business", spec_edit=None, provider_class=SqliteWorld):
    spec, catalog = fixture_spec(domain)
    if spec_edit: spec_edit(spec)
    clock = Clock()
    target = next(iter(catalog))
    constraint = next(x for x in spec["authority"] if x != target)
    provider = provider_class(tmp_path / "world.db", source="test-world", clock=clock)
    provider.seed({target: "waiting", constraint: True, "available": True,
                   "deadline": 100, "finished": False})
    store = SqlitePromiseStore(tmp_path / "promises.db")
    engine = PromiseEngine(store, provider, catalog, clock=clock)
    state = engine.draft("p", "owner", spec)
    return engine, provider, clock, state


def activate(engine, state):
    state = engine.confirm("p", "owner", state["contract_version"], state["contract_hash"])
    return engine.reconcile("p")


def approve(engine):
    state = engine.get("p", "owner")
    engine.approve("p", "owner", deepcopy(state["binding"]))
    return deepcopy(state["binding"])


def test_meaning_confirmation_is_not_action_approval(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    assert e.execute("p")["decision"] == "REQUEST_CLARIFICATION"
    s = activate(e, s)
    assert s["decision"] == "REQUEST_APPROVAL"
    e.execute("p")
    assert p.write_count() == 0
    approve(e)
    c.value = 100
    s = e.execute("p")
    assert p.write_count() == 1
    assert s["phase"] == "ACTIVE"  # a tool response is not lifetime completion
    assert s["receipts"][0]["verified"] is True


def test_assumption_change_reprojects_before_failure(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    s = activate(e, s)
    binding = approve(e)
    before = deepcopy(s["world"]["facts"])
    p.change({"available": False})
    s = e.reconcile("p")
    assert before["delivery_route"] == s["world"]["facts"]["delivery_route"] == "waiting"
    assert s["phase"] == "UNSATISFIABLE"
    assert s["threat"]["violations"] == ["route_available"]
    assert s["assumptions"]["availability"] is False
    with pytest.raises(ValueError, match="stale|terminal"): e.approve("p", "owner", binding)
    e.execute("p")
    assert p.write_count() == 0


def test_multiple_assumptions_changed_and_out_of_order_event(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    old = p.read()
    p.change({"deadline": 120, "available": False})
    latest = p.read()
    s = e.observe("p", latest)
    version = s["world_version"]
    assert e.observe("p", old)["world_version"] == version
    assert e.get("p", "owner")["world"]["facts"]["deadline"] == 120


def test_conflicting_goal_and_invariants_are_unsatisfiable(tmp_path):
    e, p, c, s = setup_engine(tmp_path, spec_edit=lambda x: x["invariants"].append(
        {"id": "never_ready", "label": "Never ready", "predicate": eq("delivery_route", "waiting")}))
    s = activate(e, s)
    assert s["phase"] == "UNSATISFIABLE"
    assert s["reason"]
    assert p.write_count() == 0


def test_conflicting_invariants_are_not_silently_dropped(tmp_path):
    e, p, c, s = setup_engine(tmp_path, spec_edit=lambda x: x["invariants"].append(
        {"id": "opposite", "label": "Conflict", "predicate": eq("budget_ok", False)}))
    assert activate(e, s)["phase"] == "UNSATISFIABLE"
    assert p.write_count() == 0


def test_new_repair_requires_new_authority(tmp_path):
    def edit(x):
        x["invariants"].append({"id": "not_early", "label": "Not before deadline", "predicate": {
            "implies": [{"lt": [{"fact": "$now"}, {"fact": "deadline"}]}, eq("delivery_route", "waiting")]}})
    e, p, c, s = setup_engine(tmp_path, spec_edit=edit)
    s = activate(e, s)
    old = approve(e)
    p.change({"deadline": 130})
    s = e.reconcile("p")
    assert s["plan_version"] > old["plan_version"]
    assert s["decision"] == "REQUEST_APPROVAL"
    assert s["threat"]["violations"] == ["not_early"]
    with pytest.raises(ValueError, match="stale"): e.approve("p", "owner", old)
    c.value = 130
    e.execute("p")
    assert p.write_count() == 0
    approve(e)
    e.execute("p")
    assert p.write_count() == 1


def test_duplicate_event_and_content_tamper(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    event = p.read()
    first = e.observe("p", event)
    assert e.observe("p", event)["world_version"] == first["world_version"]
    corrupt = deepcopy(event)
    corrupt["facts"]["available"] = False
    with pytest.raises(ValueError, match="event|snapshot"): e.observe("p", corrupt)


def test_approval_replay_and_restart_do_not_repeat_writes(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    binding = approve(e)
    e.approve("p", "owner", binding)
    c.value = 100
    e.execute("p")
    e2 = PromiseEngine(SqlitePromiseStore(tmp_path / "promises.db"), p, e.catalog, clock=c)
    e2.execute("p")
    with pytest.raises(ValueError, match="stale|used"): e2.approve("p", "owner", binding)
    assert p.write_count() == 1
    assert len(e2.get("p", "owner")["receipts"]) == 1


def test_false_tool_success_is_not_verified(tmp_path):
    class Liar(SqliteWorld):
        def apply(self, action, key, expected_revision, not_after):
            return {"ok": True, "key": key}
    e, p, c, s = setup_engine(tmp_path, provider_class=Liar)
    activate(e, s)
    approve(e)
    c.value = 100
    s = e.execute("p")
    assert s["decision"] == "VERIFY_FAILED"
    assert not any(r["verified"] for r in s["receipts"])
    assert s["phase"] != "SATISFIED"


def test_expiry_at_provider_commit_prevents_effect(tmp_path):
    class Slow(SqliteWorld):
        def apply(self, action, key, expected_revision, not_after):
            self.clock.value = 201
            return super().apply(action, key, expected_revision, not_after)
    e, p, c, s = setup_engine(tmp_path, provider_class=Slow)
    activate(e, s)
    approve(e)
    c.value = 100
    assert e.execute("p")["phase"] == "EXPIRED"
    assert p.write_count() == 0


def test_impossible_goal_without_a_tool_is_explicit(tmp_path):
    e, p, c, s = setup_engine(tmp_path, spec_edit=lambda x: x.update(goal=eq("delivery_route", "unavailable-value")))
    assert activate(e, s)["phase"] == "UNSATISFIABLE"
    assert p.write_count() == 0


def test_cheapest_unsafe_repair_is_excluded_and_tie_is_stable(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    a = activate(e, s)
    h = digest(a["plan"])
    for _ in range(3): assert digest(e.reconcile("p")["plan"]) == h
    assert all("budget_ok" not in x["writes"] for x in a["plan"]["actions"])


def test_semantic_ambiguity_blocks_activation_and_writes(tmp_path):
    e, p, c, s = setup_engine(tmp_path, spec_edit=lambda x: x.update(questions=["Which areas remain occupied?"]))
    with pytest.raises(ValueError, match="clarification"): e.confirm("p", "owner", 1, s["contract_hash"])
    assert e.execute("p")["decision"] == "REQUEST_CLARIFICATION"
    assert p.write_count() == 0


def test_semantic_revision_requires_confirmation_and_invalidates_old_approval(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    activate(e, s)
    binding = approve(e)
    revised = deepcopy(s["contract"])
    revised["meaning"] = "Corrected human meaning"
    s = e.revise("p", "owner", revised)
    assert s["contract_version"] == 2 and s["phase"] == "DRAFT"
    with pytest.raises(ValueError): e.approve("p", "owner", binding)
    e.execute("p")
    assert p.write_count() == 0


@pytest.mark.parametrize("domain", ["household", "business", "software"])
def test_same_engine_cross_domain_without_hero_rules(tmp_path, domain):
    e, p, c, s = setup_engine(tmp_path, domain)
    activate(e, s)
    approve(e)
    c.value = 100
    s = e.execute("p")
    assert s["receipts"][0]["verified"]
    p.change({"finished": True})
    assert e.reconcile("p")["phase"] == "SATISFIED"


def test_missing_evidence_is_clarification_not_unsatisfiable(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    p.change({"budget_ok": None})
    s = activate(e, s)
    assert s["decision"] == "REQUEST_CLARIFICATION"
    assert s["phase"] != "UNSATISFIABLE"
    assert p.write_count() == 0


def test_owner_boundary_and_exact_delta_binding(tmp_path):
    e, p, c, s = setup_engine(tmp_path)
    with pytest.raises(ValueError): e.get("p", "other")
    activate(e, s)
    binding = deepcopy(e.get("p", "owner")["binding"])
    binding["actions"][0]["writes"]["delivery_route"] = "injected"
    with pytest.raises(ValueError, match="stale|binding"): e.approve("p", "owner", binding)
    assert p.write_count() == 0
