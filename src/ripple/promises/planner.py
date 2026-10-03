from __future__ import annotations

from itertools import product
from math import prod
from copy import deepcopy

from .model import canonical, evaluate


def check_invariants(contract, facts, now):
    results = {p["id"]: evaluate(p["predicate"], facts, now) for p in contract["invariants"]}
    return {"at": now, "results": results,
            "violations": sorted(k for k, v in results.items() if v is False),
            "unknown": sorted(k for k, v in results.items() if type(v) is not bool)}


def project(contract, facts, actions, now):
    horizon = evaluate(contract["goal_at"], facts, now)
    if type(horizon) is not int or horizon >= contract["expiry"]["at"]:
        return {"valid": False, "unknown": ["goal_time"], "violations": [], "checks": []}
    if horizon < now and evaluate(contract["goal"], facts, now) is not True:
        return {"valid": False, "unknown": [], "violations": ["goal_deadline_missed"], "checks": [], "goal": False}
    horizon = max(now, horizon)
    working = deepcopy(facts)
    checks = []
    # Integer time is part of the contract. Check boundaries even if no action
    # occurs there: an invariant may become false solely through elapsed time.
    literals = []
    def collect(node):
        if isinstance(node, dict):
            if type(node.get("literal")) is int: literals.append(node["literal"])
            for value in node.values(): collect(value)
        elif isinstance(node, list):
            for value in node: collect(value)
    collect(contract["invariants"])
    points = {now, horizon}
    for value in list(facts.values()) + literals:
        if type(value) is int:
            points.update(t for t in (value - 1, value, value + 1) if now <= t <= horizon)
    by_time = {}
    for action in actions:
        at = max(now, action["at"])
        if at > horizon:
            return {"valid": False, "unknown": [], "violations": ["after_goal_time"], "checks": []}
        by_time.setdefault(at, []).append(action)
        points.add(at)
    # The present state must be safe. No silent repair of a pre-existing violation.
    checks.append(check_invariants(contract, working, now))
    for at in sorted(points):
        for action in by_time.get(at, []):
            working.update(action["writes"])
            checks.append(check_invariants(contract, working, at))
        checks.append(check_invariants(contract, working, at))
    violations = sorted({v for c in checks for v in c["violations"]})
    unknown = sorted({v for c in checks for v in c["unknown"]})
    goal = evaluate(contract["goal"], working, horizon)
    if type(goal) is not bool: unknown.append("goal")
    return {"valid": not violations and not unknown and goal is True,
            "violations": violations, "unknown": unknown, "goal": goal,
            "projected": working, "checks": checks}


def plan(contract, facts, catalog, previous, now, max_candidates=4096):
    horizon = evaluate(contract["goal_at"], facts, now)
    if type(horizon) is not int or horizon >= contract["expiry"]["at"]:
        return {"decision": "REQUEST_CLARIFICATION", "reason": "Missing or invalid goal time"}
    if horizon < now and evaluate(contract["goal"], facts, now) is not True:
        return {"decision": "UNSATISFIABLE", "reason": "Goal time passed without the required outcome; the deadline is not silently moved"}
    current = check_invariants(contract, facts, now)
    if current["unknown"]:
        return {"decision": "REQUEST_CLARIFICATION", "reason": "Unknown invariant evidence", "evaluation": current}
    choices = []
    for key in sorted(catalog):
        control = catalog[key]
        authority = contract["authority"].get(key, "FORBIDDEN")
        if authority in {"FORBIDDEN", "OBSERVE"}: continue
        if authority == "AUTONOMOUS_REVERSIBLE" and not control["reversible"]: continue
        options = [None]
        for value in control["values"]:
            if type(value) is type(facts.get(key)) and value == facts.get(key): continue
            for timing in control["times"]:
                options.append((key, value, now if timing == "now" else max(now, horizon)))
        choices.append(options)
    count = prod(len(x) for x in choices)
    if count > max_candidates:
        return {"decision": "REQUEST_CLARIFICATION", "reason": "Planning search limit; impossibility is not proven"}
    old = {(k, canonical(v), a["at"]) for a in previous for k, v in a["writes"].items()}
    best, unknown_seen = None, False
    for choice in product(*choices):
        grouped = {}
        for selected in choice:
            if selected is not None:
                key, value, at = selected
                grouped.setdefault(at, {})[key] = value
        actions = [{"at": at, "writes": writes} for at, writes in sorted(grouped.items())]
        result = project(contract, facts, actions, now)
        unknown_seen |= bool(result["unknown"])
        if not result["valid"]: continue
        new = {(k, canonical(v), a["at"]) for a in actions for k, v in a["writes"].items()}
        rank = (len(new.symmetric_difference(old)), len(new), canonical(actions))
        if best is None or rank < best[0]: best = (rank, actions, result)
    if best is None:
        return {"decision": "REQUEST_CLARIFICATION" if unknown_seen else "UNSATISFIABLE",
                "reason": "Unknown projection evidence" if unknown_seen else "No safe feasible plan in the declared finite action catalogue",
                "candidates_checked": count}
    return {"decision": "REPAIR", "actions": best[1], "evaluation": best[2],
            "edits": best[0][0], "candidates_checked": count}
