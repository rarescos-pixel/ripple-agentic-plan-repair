from __future__ import annotations

import hashlib
import json
import math
from typing import Any

TERMINAL = {"SATISFIED", "EXPIRED", "REVOKED", "UNSATISFIABLE"}
AUTHORITY = {"OBSERVE", "AUTONOMOUS_REVERSIBLE", "APPROVAL_REQUIRED", "FORBIDDEN"}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def scalar(value: Any) -> bool:
    return value is None or type(value) in (bool, str, int) or (type(value) is float and math.isfinite(value))


def validate_expr(expr: Any, depth: int = 0) -> None:
    if depth > 12 or not isinstance(expr, dict) or len(expr) != 1:
        raise ValueError("Invalid or excessively deep expression")
    op, args = next(iter(expr.items()))
    if op == "fact":
        if not isinstance(args, str) or not args or len(args) > 100:
            raise ValueError("Invalid fact reference")
    elif op == "literal":
        if not scalar(args): raise ValueError("Literal must be a finite scalar")
    elif op in {"eq", "ne", "lt", "le", "gt", "ge", "implies", "and", "or", "not"}:
        if not isinstance(args, list) or len(args) != (1 if op == "not" else 2):
            raise ValueError("Invalid expression arity")
        for arg in args: validate_expr(arg, depth + 1)
    else:
        raise ValueError(f"Unsupported deterministic operator: {op}")


def evaluate(expr: dict, facts: dict, now: int) -> Any:
    """Three-valued logic: None means missing/ill-typed evidence, never true."""
    op, args = next(iter(expr.items()))
    if op == "literal": return args
    if op == "fact": return now if args == "$now" else facts.get(args)
    values = [evaluate(x, facts, now) for x in args]
    if op == "not": return not values[0] if type(values[0]) is bool else None
    left, right = values
    if op == "implies":
        left = not left if type(left) is bool else None
        op = "or"
    if op in {"and", "or"}:
        if any(x is not None and type(x) is not bool for x in (left, right)): return None
        if op == "and":
            if left is False or right is False: return False
            return True if left is True and right is True else None
        if left is True or right is True: return True
        return False if left is False and right is False else None
    if left is None or right is None: return None
    numbers = type(left) in (int, float) and type(right) in (int, float)
    if type(left) is not type(right) and not numbers: return None
    if op == "eq": return left == right
    if op == "ne": return left != right
    if not numbers: return None  # no lexicographic or boolean numeric ordering
    return {"lt": left < right, "le": left <= right, "gt": left > right, "ge": left >= right}[op]


def validate_contract(spec: dict) -> None:
    required = {"goal", "goal_at", "invariants", "assumptions", "authority", "expiry", "evidence", "completion", "meaning", "questions"}
    if not isinstance(spec, dict) or set(spec) != required or len(canonical(spec)) > 16000:
        raise ValueError("Contract requires exactly the documented bounded fields")
    for key in ("goal", "goal_at", "completion"): validate_expr(spec[key])
    if not isinstance(spec["meaning"], str) or not spec["meaning"].strip(): raise ValueError("Meaning is required")
    if not isinstance(spec["questions"], list) or any(not isinstance(q, str) for q in spec["questions"]):
        raise ValueError("Clarification questions must be text")
    for collection in ("invariants", "assumptions"):
        rows = spec[collection]
        if not isinstance(rows, list) or len(rows) > 16 or (collection == "invariants" and not rows):
            raise ValueError("A bounded invariant set is required")
        ids = set()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"] or row["id"] in ids:
                raise ValueError("Predicate IDs must be unique")
            ids.add(row["id"])
            validate_expr(row["predicate"])
    authority = spec["authority"]
    if not isinstance(authority, dict) or not authority or any(x not in AUTHORITY for x in authority.values()):
        raise ValueError("Invalid authority envelope")
    expiry = spec["expiry"]
    if not isinstance(expiry, dict) or set(expiry) - {"at", "when"} or type(expiry.get("at")) is not int:
        raise ValueError("Explicit integer expiry timestamp required")
    if "when" in expiry: validate_expr(expiry["when"])
    evidence = spec["evidence"]
    if set(evidence) != {"source", "max_age_seconds"} or not isinstance(evidence["source"], str):
        raise ValueError("An evidence source is required")
    if type(evidence["max_age_seconds"]) is not int or not 1 <= evidence["max_age_seconds"] <= 86400:
        raise ValueError("Invalid evidence freshness window")


def validate_catalog(catalog: dict) -> None:
    if not isinstance(catalog, dict) or len(catalog) > 12: raise ValueError("Bounded control catalogue required")
    for key, control in catalog.items():
        if not isinstance(key, str) or key == "$now" or set(control) - {"values", "times", "reversible", "requires"} or not {"values", "times", "reversible"} <= set(control):
            raise ValueError("Invalid deployment control")
        if not isinstance(control["values"], list) or not 1 <= len(control["values"]) <= 8 or any(not scalar(v) or v is None for v in control["values"]):
            raise ValueError("Controls require finite non-null values")
        if not isinstance(control["times"], list) or not control["times"] or any(x not in {"now", "goal"} for x in control["times"]):
            raise ValueError("Unsupported action timing")
        if type(control["reversible"]) is not bool: raise ValueError("Reversibility must be declared")
        if "requires" in control: validate_expr(control["requires"])


def snapshot_hash(snapshot: dict) -> str:
    return digest({k: snapshot[k] for k in ("source", "revision", "facts")})
