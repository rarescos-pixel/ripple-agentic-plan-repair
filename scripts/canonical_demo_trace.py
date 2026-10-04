#!/usr/bin/env python3
"""Generate the deterministic truth feed for the Ripple Gate 4 film.

The film is presentation. This file is product truth.
It deliberately replays the already-accepted household continuous-promise path
using the real PromiseEngine, persistence boundary and digital-twin provider.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import tempfile

from ripple.promises.engine import PromiseEngine
from ripple.promises.examples import household
from ripple.promises.provider import SqliteWorld
from ripple.promises.store import SqlitePromiseStore


class Clock:
    def __init__(self, value: int = 1000):
        self.value = value

    def __call__(self) -> int:
        return self.value


def _snapshot(state, world: SqliteWorld, *, session_generation: int) -> dict:
    receipts = state.get("receipts") or []
    return {
        "contract_id": state["id"],
        "contract_version": state["contract_version"],
        "world_version": state["world_version"],
        "plan_version": state["plan_version"],
        "phase": state["phase"],
        "decision": state["decision"],
        "plan": deepcopy(state["plan"]),
        "binding": deepcopy(state.get("binding")),
        "approval_present": state.get("approval") is not None,
        "assumptions": deepcopy(state.get("assumptions") or {}),
        "threat": deepcopy(state.get("threat")),
        "world_facts": deepcopy((state.get("world") or {}).get("facts")),
        "write_count": world.write_count(),
        "verified_receipts": sum(1 for receipt in receipts if receipt.get("verified") is True),
        "ledger_hash": state["ledger"][-1]["hash"] if state.get("ledger") else None,
        "session_generation": session_generation,
    }


def build_trace(root: Path) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    clock = Clock(1000)
    contract, catalog, facts = household(1000)
    world = SqliteWorld(root / "world.db", source="household-twin", clock=clock)
    world.seed(facts)
    state_path = root / "promises.db"
    engine = PromiseEngine(SqlitePromiseStore(state_path), world, catalog, clock=clock)

    beats: list[dict] = []

    def beat(beat_id: str, frame: int, event: str, evidence_class: str, state: dict, session: int = 1):
        beats.append({
            "id": beat_id,
            "frame": frame,
            "event": event,
            "evidence_class": evidence_class,
            "state": _snapshot(state, world, session_generation=session),
        })

    # Human utterance becomes a draft contract. No provider effect is possible here.
    state = engine.draft("hero", "owner", contract)
    beat("draft", 300, "contract.drafted", "engine", state)

    # Meaning confirmation is human authority and remains distinct from action approval.
    state = engine.confirm("hero", "owner", state["contract_version"], state["contract_hash"])
    beat("meaning_confirmed", 540, "meaning.confirmed", "human_authority", state)

    # Establish the initial safe bounded plan and bind the first exact approval.
    state = engine.reconcile("hero")
    beat("initial_plan", 840, "plan.repaired", "engine", state)
    state = engine.approve("hero", "owner", deepcopy(state["binding"]))
    beat("initial_action_approved", 1080, "action.approved", "human_authority", state)

    # World change one: Mom goes out. The assumption changes; her access must not.
    world.change({"guest_present": False})
    state = engine.reconcile("hero")
    beat("mom_leaves", 1140, "world.guest_present.false", "world_event", state)
    beat("repair_after_mom_leaves", 1770, "plan.repaired.after_guest_change", "engine", state)
    state = engine.approve("hero", "owner", deepcopy(state["binding"]))
    beat("repair_after_mom_leaves_approved", 1950, "action.approved", "human_authority", state)

    # Execute only what is currently due. Contract remains active.
    state = engine.execute("hero")
    beat("due_repair_executed", 2070, "execute.currently_due", "engine", state)

    # World change two: departure shifts later. Same contract, new threat/repair.
    world.change({"departure_at": 1100})
    state = engine.reconcile("hero")
    beat("departure_delayed", 2190, "world.departure_at.changed", "world_event", state)
    state = engine.approve("hero", "owner", deepcopy(state["binding"]))
    beat("exact_approval", 2730, "action.approved", "human_authority", state)

    # Reaching the old departure time must not force the old plan through.
    clock.value = 1060
    state = engine.execute("hero")
    beat("old_departure_no_effect", 2880, "execute.old_departure", "engine", state)

    # A timetable is not evidence that the family actually departed.
    clock.value = 1100
    before_wait = world.write_count()
    state = engine.execute("hero")
    assert state["decision"] == "WAIT_FOR_EVIDENCE"
    assert world.write_count() == before_wait
    beat("wait_for_departure_evidence", 2970, "execute.wait_for_evidence", "engine", state)

    # Trusted evidence arrives. Reconcile creates a fresh exact binding.
    world.change({"family_departed": True})
    state = engine.reconcile("hero")
    beat("family_departed_evidence", 3240, "world.family_departed.true", "world_event", state)
    state = engine.approve("hero", "owner", deepcopy(state["binding"]))
    beat("final_exact_approval", 3290, "action.approved", "human_authority", state)
    state = engine.execute("hero")
    assert state["receipts"] and all(r.get("verified") is True for r in state["receipts"])
    beat("verified_execution", 3330, "execute.verified_readback", "engine", state)

    # New process/session boundary: reconstruct from durable state, not conversation memory.
    reconstructed = PromiseEngine(SqlitePromiseStore(state_path), world, catalog, clock=clock)
    state = reconstructed.get("hero", "owner")
    beat("session_reconstructed", 3450, "session.reconstructed.from_store", "session", state, session=2)

    # Replaying execution cannot duplicate already committed provider effects.
    writes_before_replay = world.write_count()
    state = reconstructed.execute("hero")
    writes_after_replay = world.write_count()
    assert writes_after_replay == writes_before_replay
    beat("replay_deduplicated", 3720, "execute.replay.no_duplicate_write", "session", state, session=2)

    # Explicit independent completion closes the contract without changing its meaning version.
    world.change({"departure_verified": True})
    state = reconstructed.reconcile("hero")
    assert state["phase"] == "SATISFIED"
    assert state["contract_version"] == 1
    beat("completion_verified", 3840, "contract.satisfied.independent_completion", "engine", state, session=2)

    # Product invariants that the film is allowed to visualize as facts.
    for item in beats:
        facts_at_beat = item["state"]["world_facts"]
        if facts_at_beat is not None and "guest_access" in facts_at_beat:
            assert facts_at_beat["guest_access"] is True
        assert item["state"]["contract_version"] == 1

    return {
        "schema_version": "1.0.0",
        "scenario": {
            "id": "household-continuous-promise-v1",
            "contract_id": "hero",
            "owner": "owner",
            "provider_class": "deterministic-digital-twin",
            "host_class": "simulated-alexa-plus-host",
        },
        "render": {
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "nominal_duration_frames": 4050,
        },
        "source": {
            "generator": "scripts/canonical_demo_trace.py",
            "fixture": "ripple.promises.examples.household",
            "engine_mode": "deterministic-local-proof",
        },
        "beats": beats,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--work-dir", type=Path, default=None)
    args = parser.parse_args()

    if args.work_dir is not None:
        trace = build_trace(args.work_dir)
    else:
        with tempfile.TemporaryDirectory(prefix="ripple-canonical-trace-") as tmp:
            trace = build_trace(Path(tmp))

    rendered = json.dumps(trace, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
