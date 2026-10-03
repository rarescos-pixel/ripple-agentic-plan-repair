from __future__ import annotations

from copy import deepcopy
import time

from .model import (TERMINAL, canonical, digest, evaluate, snapshot_hash,
                    validate_catalog, validate_contract)
from .planner import check_invariants, plan, project
from .provider import ProviderRejected, validate_facts
from .store import MAX_BYTES, Conflict


class PromiseEngine:
    """Trusted application service. Human methods must not be model-callable.

    A single provider is an atomic consistency domain. Cross-provider distributed
    transactions are deliberately outside this first slice's safety claim.
    """
    def __init__(self, store, provider, catalog, *, clock=None, trace=None, max_candidates=4096):
        validate_catalog(catalog)
        self.store, self.provider = store, provider
        self.catalog = deepcopy(catalog)
        self.clock = clock or (lambda: int(time.time()))
        self.trace, self.max_candidates = trace, max_candidates

    def _load(self, contract_id):
        state = self.store.load(contract_id)
        if state is None: raise ValueError("Contract not found")
        if state["catalog_hash"] != digest(self.catalog):
            raise ValueError("Deployment catalogue changed; explicit migration/reconfirmation required")
        if state["contract_hash"] != digest(state["contract"]):
            raise ValueError("Persisted contract content does not match confirmed hash")
        return state

    def get(self, contract_id, owner):
        state = self._load(contract_id)
        if state["owner"] != owner: raise ValueError("Contract not found for this owner")
        return state

    def _log(self, state, event, **data):
        if len(state["ledger"]) >= 256: raise ValueError("Promise ledger capacity reached")
        entry = {"event": event, "at": self.clock(), "contract_version": state["contract_version"],
                 "world_version": state["world_version"], "plan_version": state["plan_version"],
                 "data": data, "previous": state["ledger"][-1]["hash"] if state["ledger"] else None}
        entry["hash"] = digest(entry)
        state["ledger"].append(entry)

    def _save(self, state):
        latest_hash = state["ledger"][-1]["hash"] if state["ledger"] else None
        new_trace = state.get("trace_hash") != latest_hash
        state["trace_hash"] = latest_hash
        old = state["revision"]
        state["revision"] += 1
        self.store.save(state, old)
        if self.trace and new_trace:
            try:
                self.trace.emit("promise.state", correlation_id=state["id"], payload={
                    "phase": state["phase"], "decision": state["decision"],
                    "contract_version": state["contract_version"], "world_version": state["world_version"],
                    "plan_version": state["plan_version"], "ledger_hash": state["ledger"][-1]["hash"],
                })
            except Exception:
                # Observability availability must not change committed authority.
                pass
        return deepcopy(state)

    def draft(self, contract_id, owner, contract):
        validate_contract(contract)
        if not isinstance(contract_id, str) or not contract_id or len(contract_id) > 100 or not owner:
            raise ValueError("Contract ID and owner required")
        state = {"id": contract_id, "owner": owner, "revision": 0,
                 "contract": deepcopy(contract), "contract_hash": digest(contract), "contract_version": 1,
                 "catalog_hash": digest(self.catalog), "world": None, "world_version": 0,
                 "execution_conditions": {k: deepcopy(v["requires"]) for k, v in self.catalog.items() if "requires" in v},
                 "plan": {"actions": []}, "plan_version": 0, "binding": None, "approval": None,
                 "confirmation": None, "phase": "DRAFT", "decision": "REQUEST_CLARIFICATION",
                 "reason": "Confirm consequential meaning before activation",
                 "assumptions": {}, "threat": None, "evaluation": None, "pending": None,
                 "goal_evidence": None,
                 "blocked": False, "receipts": [], "used_approvals": [], "ledger": [], "seen": {}}
        self._log(state, "contract.drafted", contract_hash=state["contract_hash"])
        return self._save(state)

    def revise(self, contract_id, owner, contract):
        validate_contract(contract)
        state = self.get(contract_id, owner)
        if state["pending"]: raise ValueError("Recover pending effect before revising meaning")
        if state["phase"] in TERMINAL: raise ValueError("Terminal contract; create a new contract")
        state.update(contract=deepcopy(contract), contract_hash=digest(contract),
                     contract_version=state["contract_version"] + 1, phase="DRAFT",
                     decision="REQUEST_CLARIFICATION", confirmation=None, approval=None,
                     binding=None, plan={"actions": []}, blocked=False, goal_evidence=None)
        self._log(state, "contract.revised", contract_hash=state["contract_hash"])
        return self._save(state)

    def confirm(self, contract_id, owner, version, contract_hash):
        state = self.get(contract_id, owner)
        if state["phase"] != "DRAFT": raise ValueError("Meaning can only be confirmed from DRAFT")
        if self.clock() >= state["contract"]["expiry"]["at"]: raise ValueError("Draft meaning has expired")
        if version != state["contract_version"] or contract_hash != state["contract_hash"]:
            raise ValueError("Stale meaning confirmation")
        if state["contract"]["questions"]: raise ValueError("Unresolved semantic clarification required")
        state.update(phase="ACTIVE", decision="REPAIR", confirmation={"owner": owner, "version": version, "hash": contract_hash})
        self._log(state, "meaning.confirmed", confirmation=state["confirmation"])
        return self._save(state)

    def _expired(self, state):
        expiry = state["contract"]["expiry"]
        if self.clock() >= expiry["at"]: return True
        if "when" in expiry:
            return evaluate(expiry["when"], (state["world"] or {}).get("facts", {}), self.clock())
        return False

    def _terminal(self, state, phase, reason):
        state.update(phase=phase, decision=phase, reason=reason, approval=None)
        self._log(state, "contract.terminal", outcome=phase, reason=reason)
        return self._save(state)

    def revoke(self, contract_id, owner):
        state = self.get(contract_id, owner)
        if state["pending"]: raise ValueError("Effect outcome pending; recover before revocation")
        if state["phase"] in TERMINAL: return state
        return self._terminal(state, "REVOKED", "Explicit owner revocation")

    def _accept(self, state, snapshot):
        validate_facts(snapshot["facts"])
        if snapshot["source"] != state["contract"]["evidence"]["source"]:
            raise ValueError("Untrusted evidence source")
        if type(snapshot["revision"]) is not int or snapshot["revision"] < 1:
            raise ValueError("Invalid snapshot revision")
        if type(snapshot["observed_at"]) is not int or snapshot["observed_at"] > self.clock():
            raise ValueError("Invalid snapshot observation time")
        expected_id = f'{snapshot["source"]}:{snapshot["revision"]}'
        if snapshot["event_id"] != expected_id or snapshot["snapshot_hash"] != snapshot_hash(snapshot):
            raise ValueError("Event snapshot hash mismatch")
        seen = state["seen"].get(expected_id)
        if seen and seen != snapshot["snapshot_hash"]: raise ValueError("Conflicting event at same revision")
        if state["world"] and snapshot["revision"] < state["world"]["revision"]: return False
        if seen:
            # A fresh independent read can refresh evidence without changing the
            # world's semantic version or revoking an otherwise exact approval.
            state["world"]["observed_at"] = max(state["world"]["observed_at"], snapshot["observed_at"])
            return False
        if len(state["seen"]) >= 256: raise ValueError("Promise event capacity reached")
        state["seen"][expected_id] = snapshot["snapshot_hash"]
        state["world"] = deepcopy(snapshot)
        state["world_version"] += 1
        state["approval"] = None
        state["binding"] = None
        self._log(state, "world.observed", event_id=expected_id, snapshot_hash=snapshot["snapshot_hash"])
        return True

    def observe(self, contract_id, snapshot):
        state = self._load(contract_id)
        if state["pending"]: raise ValueError("Recover pending effect before accepting a new event")
        if state["phase"] in TERMINAL: return state
        if self._accept(state, snapshot): return self._save(state)
        return state

    def _binding(self, state):
        return {"contract_id": state["id"], "owner": state["owner"],
                "catalog_hash": state["catalog_hash"],
                "execution_conditions": deepcopy(state["execution_conditions"]),
                "contract_version": state["contract_version"], "contract_hash": state["contract_hash"],
                "world_version": state["world_version"], "plan_version": state["plan_version"],
                "plan_hash": digest(state["plan"]), "actions": deepcopy(state["plan"]["actions"])}

    def reconcile(self, contract_id):
        state = self._load(contract_id)
        if state["phase"] in TERMINAL or state["blocked"]: return state
        if state["phase"] == "DRAFT":
            if self.clock() >= state["contract"]["expiry"]["at"]:
                return self._terminal(state, "EXPIRED", "Unconfirmed meaning reached its explicit expiry")
            return state
        if state["pending"]:
            state["decision"] = "RECOVERY_REQUIRED"
            return state
        changed = self._accept(state, self.provider.read())
        expired = self._expired(state)
        if expired is True: return self._terminal(state, "EXPIRED", "Explicit expiry reached")
        facts, contract, now = state["world"]["facts"], state["contract"], self.clock()
        if expired is None or now - state["world"]["observed_at"] > contract["evidence"]["max_age_seconds"]:
            state.update(decision="REQUEST_CLARIFICATION", approval=None, reason="Expiry or evidence freshness is unknown")
            return self._save(state)
        state["assumptions"] = {a["id"]: evaluate(a["predicate"], facts, now) for a in contract["assumptions"]}
        current = check_invariants(contract, facts, now)
        state["current_evaluation"] = current
        horizon = evaluate(contract["goal_at"], facts, now)
        goal_now = evaluate(contract["goal"], facts, now)
        proven = state["goal_evidence"] and state["goal_evidence"]["goal_at"] == horizon
        if goal_now is True and type(horizon) is int and now <= horizon and not current["violations"] and not current["unknown"] and not proven:
            state["goal_evidence"] = {"goal_at": horizon, "verified_at": now, "world_version": state["world_version"], "snapshot_hash": state["world"]["snapshot_hash"]}
            self._log(state, "goal.observed", evidence=state["goal_evidence"])
            proven = True
        if type(horizon) is int and horizon < now and not proven and goal_now is not False:
            state.update(decision="REQUEST_CLARIFICATION", approval=None, reason="No independent evidence proves that the goal was met by its deadline")
            return self._save(state)
        if evaluate(contract["completion"], facts, now) is True and goal_now is True and proven and not current["violations"] and not current["unknown"]:
            return self._terminal(state, "SATISFIED", "Independent completion, goal and invariant evidence")
        projection_contract = contract
        if proven and type(horizon) is int and horizon < now:
            # The deadline was actually met. Continue preserving the outcome;
            # do not turn subsequent reconciliation into a new missed deadline.
            projection_contract = {**contract, "goal_at": {"literal": now}}
        remaining = []
        for action in state["plan"]["actions"]:
            writes = {k: v for k, v in action["writes"].items() if type(facts.get(k)) is not type(v) or facts.get(k) != v}
            if writes: remaining.append({**action, "writes": writes})
        if remaining != state["plan"]["actions"]:
            state["plan"] = {"actions": remaining}
            state["plan_version"] += 1
            state["approval"] = None
            state["binding"] = None
            self._log(state, "plan.obsolete_effects_removed", actions=remaining)
        old_actions = state["plan"]["actions"]
        projected = project(projection_contract, facts, old_actions, now)
        if old_actions and not projected["valid"]:
            threat = {"world_version": state["world_version"], "plan_version": state["plan_version"],
                      "violations": projected["violations"], "unknown": projected["unknown"], "goal": projected.get("goal")}
            if threat != state["threat"]:
                state["threat"] = threat
                self._log(state, "plan.threatened", projection=threat)
            state["phase"] = "THREATENED"
        result = ({"decision": "REPAIR", "actions": old_actions, "evaluation": projected, "edits": 0}
                  if projected["valid"] else plan(projection_contract, facts, self.catalog, old_actions, now, self.max_candidates))
        if result["decision"] == "UNSATISFIABLE": return self._terminal(state, "UNSATISFIABLE", result["reason"])
        if result["decision"] == "REQUEST_CLARIFICATION":
            state.update(decision="REQUEST_CLARIFICATION", reason=result["reason"], approval=None)
            return self._save(state)
        proposal = {"actions": result["actions"]}
        if proposal != state["plan"] or state["plan_version"] == 0:
            state["plan"] = deepcopy(proposal)
            state["plan_version"] += 1
            state["approval"] = None
            self._log(state, "plan.repaired", actions=proposal["actions"], edits=result["edits"])
        state["binding"] = self._binding(state)
        state["evaluation"] = result["evaluation"]
        needs_approval = any(contract["authority"].get(k) == "APPROVAL_REQUIRED" for a in proposal["actions"] for k in a["writes"])
        approved = state["approval"] == state["binding"]
        state.update(phase="ACTIVE", decision="REQUEST_APPROVAL" if needs_approval and not approved else ("REPAIR" if proposal["actions"] else "WAIT"),
                     reason="Safe bounded plan; contract remains active until explicit completion or expiry")
        if changed: self._log(state, "world.reconciled", assumptions=state["assumptions"], decision=state["decision"])
        return self._save(state)

    def approve(self, contract_id, owner, binding):
        state = self.get(contract_id, owner)
        if state["phase"] in TERMINAL: raise ValueError("Cannot approve a terminal contract")
        if state["phase"] == "DRAFT" or not state["binding"] or binding != state["binding"] or binding != self._binding(state) or digest(binding) in state["used_approvals"]:
            raise ValueError("stale or used approval binding")
        if self._expired(state) is not False or state["blocked"] or state["pending"]:
            raise ValueError("Approval unavailable while expired or recovery is required")
        if not binding["actions"]: raise ValueError("No consequential delta to approve")
        if state["approval"] == binding: return state
        state.update(approval=deepcopy(binding), decision="REPAIR")
        self._log(state, "action.approved", binding=deepcopy(binding))
        return self._save(state)

    def _capacity(self, state):
        # Reserve sufficient room for a bounded read-back/receipt and its ledger
        # before the external effect, including the largest accepted snapshot.
        if len(canonical(state).encode()) > MAX_BYTES - 65000 or len(state["ledger"]) > 240 or len(state["seen"]) > 250:
            raise ValueError("Promise capacity insufficient for an execution receipt")

    def execute(self, contract_id):
        state = self._load(contract_id)
        if state["pending"]: return self._recover(state)
        state = self.reconcile(contract_id)
        if state["phase"] != "ACTIVE" or state["decision"] not in {"REPAIR", "WAIT"}: return state
        due = [a for a in state["plan"]["actions"] if a["at"] <= self.clock()]
        if not due: return state
        self._capacity(state)
        action = deepcopy(due[0])
        for key, value in action["writes"].items():
            control = self.catalog.get(key)
            permission = state["contract"]["authority"].get(key, "FORBIDDEN")
            if control is None or not any(type(value) is type(v) and value == v for v in control["values"]):
                raise ValueError("Effect outside deployment control catalogue")
            if permission in {"FORBIDDEN", "OBSERVE"}: raise ValueError("Effect forbidden")
            if permission == "AUTONOMOUS_REVERSIBLE" and not control["reversible"]: raise ValueError("Effect is not reversible")
            if permission == "APPROVAL_REQUIRED" and state["approval"] != state["binding"]: raise ValueError("Exact action approval required")
        # The same deterministic constraints also run at the provider's atomic
        # commit boundary. A clock tick during network I/O cannot bypass them.
        action["guard"] = {"invariants": deepcopy(state["contract"]["invariants"]),
                           "expiry": deepcopy(state["contract"]["expiry"]),
                           "preconditions": [deepcopy(self.catalog[k]["requires"]) for k in action["writes"] if "requires" in self.catalog[k]]}
        next_facts = {**state["world"]["facts"], **action["writes"]}
        if any(evaluate(predicate, next_facts, self.clock()) is not True for predicate in action["guard"]["preconditions"]):
            state.update(decision="WAIT_FOR_EVIDENCE", reason="A deployment execution condition is not independently observed; no effect authorized yet")
            return self._save(state)
        key = digest({"binding": state["binding"], "action": action})
        horizon = evaluate(state["contract"]["goal_at"], state["world"]["facts"], self.clock())
        previously_met = state["goal_evidence"] and state["goal_evidence"]["goal_at"] == horizon
        not_after = state["contract"]["expiry"]["at"] if previously_met else min(state["contract"]["expiry"]["at"], horizon + 1)
        pending = {"key": key, "action": action, "binding": deepcopy(state["binding"]),
                   "before": deepcopy(state["world"]), "not_after": not_after,
                   "approval_mode": "exact" if state["approval"] else "confirmed_reversible_envelope"}
        state["pending"] = pending
        self._log(state, "effect.reserved", key=key, binding_hash=digest(state["binding"]))
        state = self._save(state)  # CAS winner only; persist intent BEFORE I/O
        return self._recover(state)

    def _recover(self, state):
        pending = state["pending"]
        key = pending["key"]
        try:
            receipt = self.provider.lookup(key)
            if receipt is None:
                # A recovery never acquires a new approval or a new operation key.
                receipt = self.provider.apply(pending["action"], key, pending["before"]["revision"], pending["not_after"])
            after = self.provider.read()  # independent, not the apply response
        except ProviderRejected as exc:
            state["pending"] = None
            state["approval"] = None
            self._log(state, "effect.rejected", key=key, reason=str(exc))
            if self._expired(state) is True: return self._terminal(state, "EXPIRED", str(exc))
            state.update(decision="REPAIR", reason=str(exc))
            return self._save(state)
        except Exception as exc:
            state.update(decision="RECOVERY_REQUIRED", reason=f"Uncertain provider outcome: {type(exc).__name__}")
            return self._save(state)
        expected = {**pending["before"]["facts"], **pending["action"]["writes"]}
        check = check_invariants(state["contract"], after["facts"], self.clock())
        verified = (receipt.get("key") == key and receipt.get("after_hash") == digest(expected)
                    and receipt.get("before_hash") == digest(pending["before"]["facts"])
                    and receipt.get("revision_before") == pending["before"]["revision"]
                    and receipt.get("revision_after") == after["revision"] == pending["before"]["revision"] + 1
                    and type(receipt.get("applied_at")) is int and receipt["applied_at"] < pending["not_after"]
                    and pending["action"]["at"] <= receipt["applied_at"] <= after["observed_at"]
                    and after["facts"] == expected and not check["violations"] and not check["unknown"])
        result = {"key": key, "binding": pending["binding"], "action": pending["action"],
                  "approval_mode": pending["approval_mode"], "provider_receipt": receipt,
                  "before": pending["before"], "independent_readback": after,
                  "invariant_evaluation": check, "verified": verified}
        state["pending"] = None
        state["receipts"].append(result)
        state["used_approvals"].append(digest(pending["binding"]))
        state["approval"] = None
        self._accept(state, after)
        self._log(state, "effect.verified" if verified else "effect.unverified", key=key, receipt_hash=digest(result))
        if not verified:
            state.update(blocked=True, phase="THREATENED", decision="VERIFY_FAILED", reason="Independent read-back did not prove the exact authorized transition")
            return self._save(state)
        executed_action = {k: v for k, v in pending["action"].items() if k != "guard"}
        state["plan"]["actions"] = [a for a in state["plan"]["actions"] if a != executed_action]
        # The next proposal/binding is always published by reconciliation.
        state["binding"] = None
        state["plan_version"] += 1
        state = self._save(state)
        return self.reconcile(state["id"])
