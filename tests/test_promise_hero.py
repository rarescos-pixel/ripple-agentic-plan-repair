from copy import deepcopy

from test_promise_acceptance import Clock
from ripple.promises.engine import PromiseEngine
from ripple.promises.examples import household
from ripple.promises.planner import project
from ripple.promises.provider import SqliteWorld
from ripple.promises.store import SqlitePromiseStore


def test_hero_preserves_four_invariants_across_two_changes(tmp_path):
    clock = Clock()
    clock.value = 1000
    spec, catalog, facts = household()
    world = SqliteWorld(tmp_path / "world.db", source="household-twin", clock=clock)
    world.seed(facts)
    e = PromiseEngine(SqlitePromiseStore(tmp_path / "state.db"), world, catalog, clock=clock)
    naive = project(spec, facts, [{"at": 1060, "writes": {"common_mode": "away", "guest_heat": "eco", "alarm_mode": "full"}}], 1000)
    assert set(naive["violations"]) == {"occupied_comfort", "occupied_security"}
    s = e.draft("hero", "owner", spec)
    e.confirm("hero", "owner", 1, s["contract_hash"])
    s = e.reconcile("hero")
    assert s["plan"]["actions"] == [{"at": 1060, "writes": {"common_mode": "away"}}]
    e.approve("hero", "owner", s["binding"])
    world.change({"guest_present": False})
    s = e.reconcile("hero")
    assert s["decision"] == "REQUEST_APPROVAL"
    assert s["assumptions"]["guest_stays"] is False
    assert s["world"]["facts"]["guest_access"] is True
    e.approve("hero", "owner", s["binding"])
    # Execute the currently due bounded repair, then preserve the same contract.
    s = e.execute("hero")
    assert s["phase"] == "ACTIVE"
    world.change({"departure_at": 1100})
    s = e.reconcile("hero")
    assert "departure_timing" in s["threat"]["violations"]
    assert s["decision"] == "REQUEST_APPROVAL"
    e.approve("hero", "owner", s["binding"])
    clock.value = 1060
    e.execute("hero")
    assert world.read()["facts"]["common_mode"] == "home"
    clock.value = 1100
    # A timetable is not proof that people actually left.
    held = e.execute("hero")
    assert held["decision"] == "WAIT_FOR_EVIDENCE"
    assert world.read()["facts"]["alarm_mode"] == "stay"
    world.change({"family_departed": True})
    s = e.reconcile("hero")
    e.approve("hero", "owner", s["binding"])
    s = e.execute("hero")
    assert s["receipts"] and all(r["verified"] for r in s["receipts"])
    before = world.write_count()
    e.execute("hero")
    assert world.write_count() == before
    world.change({"departure_verified": True})
    s = e.reconcile("hero")
    assert s["phase"] == "SATISFIED" and s["contract_version"] == 1
    assert all(all(v is True for v in r["invariant_evaluation"]["results"].values()) for r in s["receipts"])
