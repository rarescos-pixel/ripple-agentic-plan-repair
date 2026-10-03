"""Durable bounded watchlist, independent of conversational/MCP sessions."""
from __future__ import annotations

from .model import TERMINAL
from .store import Conflict

WATCHLIST = "__promise_watchlist__"


class PromiseWorker:
    def __init__(self, engine): self.engine = engine

    def register(self, contract_id):
        if contract_id.startswith("__"): raise ValueError("Reserved contract identifier")
        for _ in range(5):
            state = self.engine.store.load(WATCHLIST) or {"id": WATCHLIST, "revision": 0, "contracts": []}
            if contract_id in state["contracts"]: return
            if len(state["contracts"]) >= 32: raise ValueError("Bounded worker capacity reached")
            old = state["revision"]
            state["revision"] += 1
            state["contracts"].append(contract_id)
            try:
                self.engine.store.save(state, old)
                return
            except Conflict: continue
        raise Conflict("Watchlist changed concurrently; retry registration")

    def tick(self):
        try: watchlist = self.engine.store.load(WATCHLIST) or {"contracts": []}
        except Exception as exc:
            return {"_worker": {"decision": "BLOCKED", "reason": type(exc).__name__}}
        result = {}
        terminal = set()
        for contract_id in watchlist["contracts"]:
            try:
                state = self.engine.execute(contract_id)
                result[contract_id] = {"phase": state["phase"], "decision": state["decision"]}
                if state["phase"] in TERMINAL: terminal.add(contract_id)
            except Exception as exc:
                # A provider outage must not permanently kill the observation
                # loop. Pending reservations remain durable for the next tick.
                result[contract_id] = {"decision": "BLOCKED", "reason": type(exc).__name__}
        if terminal:
            old = watchlist["revision"]
            watchlist["contracts"] = [c for c in watchlist["contracts"] if c not in terminal]
            watchlist["revision"] += 1
            try: self.engine.store.save(watchlist, old)
            except Exception:
                # A concurrent registration wins. Leave terminal IDs for the
                # next tick, rather than dropping the newly registered work.
                pass
        return result
