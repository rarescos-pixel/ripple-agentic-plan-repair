"""Conditional digital-twin provider. Physical device adapters are not implied."""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from .model import canonical, digest, evaluate, scalar, snapshot_hash


class ProviderRejected(ValueError):
    pass


def validate_facts(facts):
    if not isinstance(facts, dict) or len(facts) > 64 or len(canonical(facts)) > 8000:
        raise ValueError("World snapshot exceeds bounded schema")
    if any(not isinstance(k, str) or not k or k == "$now" or not scalar(v) for k, v in facts.items()):
        raise ValueError("World facts must be named finite scalars")


class SqliteWorld:
    def __init__(self, path, *, source, clock=None):
        self.path, self.source = str(path), source
        self.clock = clock or (lambda: int(time.time()))
        Path(self.path).resolve().parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS world (id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER, facts TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS world_writes (key TEXT PRIMARY KEY, request_hash TEXT, receipt TEXT)")

    def seed(self, facts):
        validate_facts(facts)
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT OR IGNORE INTO world VALUES (1, 1, ?)", (canonical(facts),))

    def read(self):
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT revision, facts FROM world WHERE id=1").fetchone()
        if not row: raise ValueError("Provider world is not initialized")
        result = {"source": self.source, "revision": row[0], "facts": json.loads(row[1]), "observed_at": self.clock()}
        result["event_id"] = f"{self.source}:{row[0]}"
        result["snapshot_hash"] = snapshot_hash(result)
        return result

    def change(self, patch):
        """Trusted scenario/event adapter; never exposed as an MCP model tool."""
        with sqlite3.connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            revision, raw = db.execute("SELECT revision, facts FROM world WHERE id=1").fetchone()
            facts = json.loads(raw)
            facts.update(patch)
            validate_facts(facts)
            db.execute("UPDATE world SET revision=?, facts=? WHERE id=1", (revision + 1, canonical(facts)))

    def lookup(self, key):
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT receipt FROM world_writes WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else None

    def apply(self, action, key, expected_revision, not_after):
        request_hash = digest({"action": action, "expected_revision": expected_revision, "not_after": not_after})
        with sqlite3.connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT request_hash, receipt FROM world_writes WHERE key=?", (key,)).fetchone()
            if row:
                if row[0] != request_hash: raise ProviderRejected("Idempotency key content mismatch")
                return json.loads(row[1])
            now = self.clock()
            if now >= not_after: raise ProviderRejected("Expired at provider commit boundary")
            if now < action["at"]: raise ProviderRejected("Action is not due")
            revision, raw = db.execute("SELECT revision, facts FROM world WHERE id=1").fetchone()
            if revision != expected_revision: raise ProviderRejected("World revision changed before effect")
            before = json.loads(raw)
            after = {**before, **action["writes"]}
            validate_facts(after)
            guard = action.get("guard")
            if not guard: raise ProviderRejected("Deterministic commit guard required")
            expiry = guard["expiry"]
            if now >= expiry["at"] or ("when" in expiry and evaluate(expiry["when"], before, now) is not False):
                raise ProviderRejected("Expired or unknown expiry at commit boundary")
            for predicate in guard["invariants"]:
                if any(evaluate(predicate["predicate"], facts, now) is not True for facts in (before, after)):
                    raise ProviderRejected("Invariant would fail at commit boundary")
            if any(evaluate(predicate, after, now) is not True for predicate in guard.get("preconditions", [])):
                raise ProviderRejected("Execution condition missing at commit boundary")
            receipt = {"key": key, "request_hash": request_hash, "applied_at": now,
                       "revision_before": revision, "revision_after": revision + 1,
                       "before_hash": digest(before), "after_hash": digest(after)}
            db.execute("UPDATE world SET revision=?, facts=? WHERE id=1", (revision + 1, canonical(after)))
            db.execute("INSERT INTO world_writes VALUES (?, ?, ?)", (key, request_hash, canonical(receipt)))
        return receipt

    def write_count(self):
        with sqlite3.connect(self.path) as db:
            return db.execute("SELECT COUNT(*) FROM world_writes").fetchone()[0]
