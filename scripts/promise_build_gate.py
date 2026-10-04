#!/usr/bin/env python3
"""Reproduce the first build gate across an actual HTTP process boundary.

No physical home, Alexa host or live Bedrock claim is made. Scenario time and
semantic normalization are explicit fixtures; execution, persistence, HTTP,
approval separation, read-back and worker reconciliation run as real code.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time

from starlette.applications import Starlette
from starlette.testclient import TestClient
from ripple.promises.engine import PromiseEngine
from ripple.promises.examples import HERO_UTTERANCE, household
from ripple.promises.interface import PromiseService, human_routes
from ripple.promises.model import digest
from ripple.promises.planner import project
from ripple.promises.provider import SqliteWorld
from ripple.promises.provider_http import HttpWorld
from ripple.promises.store import SqlitePromiseStore
from ripple.promises.worker import PromiseWorker


def run_gate():
    with tempfile.TemporaryDirectory(prefix="ripple-promise-proof-") as directory:
        root = Path(directory)
        clock_file = root / "clock"
        clock_file.write_text("1000")
        clock = lambda: int(clock_file.read_text())
        contract, catalog, initial = household()
        fixture = SqliteWorld(root / "world.db", source="household-twin", clock=clock)
        fixture.seed(initial)
        token = secrets.token_urlsafe(32)
        human_token = secrets.token_urlsafe(32)
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        env = dict(os.environ, RIPPLE_PROMISE_PROVIDER_TOKEN=token)
        command = [sys.executable, "-m", "ripple.promises.provider_http", "--database", str(root / "world.db"),
                   "--source", "household-twin", "--port", str(port), "--clock-file", str(clock_file)]
        process = subprocess.Popen(command, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            remote = HttpWorld(f"http://127.0.0.1:{port}", token)
            for _ in range(100):
                try:
                    remote.read()
                    break
                except Exception:
                    if process.poll() is not None: raise RuntimeError("Provider failed to start")
                    time.sleep(.03)
            else: raise RuntimeError("Provider readiness deadline exceeded")
            store = SqlitePromiseStore(root / "promises.db")
            engine = PromiseEngine(store, remote, catalog, clock=clock)
            worker = PromiseWorker(engine)
            # This is a reviewed contract fixture, not a recorded/live LLM result.
            service = PromiseService(engine, None, "fixture-human", human_token)
            app = Starlette(routes=human_routes(lambda request: service))
            steps = []
            def capture(label):
                state = engine.get("hero", "fixture-human")
                steps.append({"label": label, "at": clock(), "phase": state["phase"], "decision": state["decision"],
                              "contract_version": state["contract_version"], "world_version": state["world_version"],
                              "plan_version": state["plan_version"], "world": remote.read(), "plan": deepcopy(state["plan"]),
                              "binding": deepcopy(state["binding"]), "threat": deepcopy(state["threat"]),
                              "external_writes": fixture.write_count()})
                return state
            with TestClient(app) as review:
                human_headers = {"Authorization": "Bearer " + human_token}
                state = engine.draft("hero", "fixture-human", contract)
                worker.register("hero")
                capture("draft_meaning")
                denied = review.post("/promises/human/hero/confirm", headers={"Authorization": "Bearer model-token"},
                    json={"contract_version": 1, "contract_hash": state["contract_hash"]})
                assert denied.status_code == 401
                approved = review.post("/promises/human/hero/confirm", headers=human_headers,
                    json={"contract_version": 1, "contract_hash": state["contract_hash"]})
                assert approved.status_code == 200
                worker.tick()
                state = capture("partial_transition_proposed")
                assert fixture.write_count() == 0 and state["decision"] == "REQUEST_APPROVAL"
                def approve_current():
                    binding = engine.get("hero", "fixture-human")["binding"]
                    response = review.post("/promises/human/hero/approve", headers=human_headers, json={"binding": binding})
                    assert response.status_code == 200, response.text
                    return deepcopy(binding)
                first_binding = approve_current()
                clock_file.write_text("1010")
                fixture.change({"guest_present": False})
                worker.tick()
                state = capture("occupancy_change_reconciled")
                assert state["world"]["facts"]["guest_access"] is True
                stale = review.post("/promises/human/hero/approve", headers=human_headers, json={"binding": first_binding})
                assert stale.status_code == 409
                approve_current()
                worker.tick()
                capture("empty_guest_area_repaired")
                clock_file.write_text("1020")
                fixture.change({"departure_at": 1100})
                # A reconstructed worker has no chat session or prior in-memory plan.
                engine = PromiseEngine(SqlitePromiseStore(root / "promises.db"), remote, catalog, clock=clock)
                worker = PromiseWorker(engine)
                service.engine = engine
                worker.tick()
                state = capture("departure_change_detected_before_violation")
                assert "departure_timing" in state["threat"]["violations"]
                approve_current()
                clock_file.write_text("1060")
                worker.tick()
                state = capture("old_departure_time_no_premature_effect")
                assert state["world"]["facts"]["common_mode"] == "home"
                clock_file.write_text("1100")
                worker.tick()
                state = capture("wait_for_actual_family_departure")
                assert state["decision"] == "WAIT_FOR_EVIDENCE"
                fixture.change({"family_departed": True})
                worker.tick()
                approve_current()
                worker.tick()
                capture("verified_departure_transition")
                before_replay = fixture.write_count()
                for _ in range(5): worker.tick()
                replay_writes = fixture.write_count() - before_replay
                assert replay_writes == 0
                fixture.change({"departure_verified": True})
                worker.tick()
                state = capture("satisfied_after_independent_completion")
                assert state["phase"] == "SATISFIED"
            naive = project(contract, initial, [{"at": 1060, "writes": {"common_mode": "away", "guest_heat": "eco", "alarm_mode": "full"}}], 1000)
            receipts = state["receipts"]
            evaluations = [r["invariant_evaluation"] for r in receipts]
            invariant_violations = sum(len(x["violations"]) for x in evaluations)
            unverified = sum(not r["verified"] for r in receipts)
            authorized = {digest(x["data"]["binding"]) for x in state["ledger"] if x["event"] == "action.approved"}
            unauthorized = sum(digest(r["binding"]) not in authorized for r in receipts)
            assert receipts and invariant_violations == unverified == unauthorized == replay_writes == 0
            assert fixture.write_count() == len(receipts)
            previous = None
            for entry in state["ledger"]:
                assert entry["previous"] == previous
                assert entry["hash"] == digest({k: v for k, v in entry.items() if k != "hash"})
                previous = entry["hash"]
            source_files = sorted(Path("src/ripple/promises").glob("*.py"))
            return {
                "schema": "ripple.promise-build-gate.v1", "gate": "PASS",
                "scope": "Separate HTTP digital-twin provider, SQLite durability, deterministic scenario clock; not physical Alexa/device or live Bedrock validation",
                "source_digest": digest({str(p): p.read_text() for p in source_files}),
                "human_intent_fixture": HERO_UTTERANCE,
                "normalization": "Reviewed structured fixture; live Bedrock remains a separate gate",
                "contract": contract, "catalog": catalog, "initial_world": initial,
                "naive_plan_prediction": naive,
                "metrics": {"contract_versions": state["contract_version"], "confirmed_invariants": len(contract["invariants"]),
                            "verified_external_writes": fixture.write_count(), "verified_receipts": len(receipts),
                            "invariant_violations_at_verified_transitions": invariant_violations,
                            "unauthorized_effects": unauthorized, "unverified_effects": unverified,
                            "duplicate_writes_in_five_replays": replay_writes,
                            "reconciliation_events": sum(x["event"] == "world.reconciled" for x in state["ledger"]),
                            "terminal_state": state["phase"]},
                "steps": steps, "receipts": receipts, "ledger": state["ledger"],
            }
        finally:
            process.terminate()
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="docs/PROMISE_BUILD_EVIDENCE.json")
    args = parser.parse_args()
    result = run_gate()
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"gate": result["gate"], "metrics": result["metrics"], "scope": result["scope"]}, indent=2))


if __name__ == "__main__": main()
