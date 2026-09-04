from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Dict, Any
from datetime import datetime, timedelta
import re
from ripple.domain.models import ChangeEvent, RepairPlan
from ripple.orchestration.planner import Planner


class ChangeInterpreter(Protocol):
    """Pluggable intelligence boundary. A Bedrock-backed implementation can replace this later."""
    def interpret(self, utterance: str, context: Dict[str, Any]) -> ChangeEvent: ...


@dataclass
class GoldenChangeInterpreter:
    """Small deterministic flight-change interpreter for the local demo.

    This is intentionally *not* presented as general NLP. Unlike the old fixture,
    it does parse the time the user actually said, so changing 18:00 to 23:55
    changes the canonical ChangeEvent and the repair plan. Bedrock can replace
    this boundary without changing the deterministic planner/executor.
    """
    def interpret(self, utterance: str, context: Dict[str, Any]) -> ChangeEvent:
        normalized = utterance.lower().strip()
        if "flight" not in normalized or "cancel" not in normalized:
            raise ValueError("Utterance is outside the v0.3 golden interpreter contract (deterministic flight-change demo)")

        match = re.search(r"(?:at\s+)?([01]?\d|2[0-3]):([0-5]\d)", normalized)
        if not match:
            raise ValueError("State the new arrival time as HH:MM")
        hour, minute = map(int, match.groups())

        old_dt = datetime.fromisoformat(context["old_arrival_at"])
        if "tomorrow" in normalized:
            new_date = old_dt.date() + timedelta(days=1)
        else:
            target = context.get("target_arrival_date")
            if not target:
                raise ValueError("State 'tomorrow' or provide target_arrival_date in canonical context")
            new_date = datetime.fromisoformat(target).date()
        new_dt = datetime.combine(new_date, datetime.min.time()).replace(hour=hour, minute=minute)

        change_id = context.get("change_id") or f"change:flight-arrival:{new_dt.isoformat()}"
        return ChangeEvent(
            id=change_id,
            node_id="flight:return",
            field="arrival_at",
            old_value=context["old_arrival_at"],
            new_value=new_dt.isoformat(),
            source="voice",
            confidence=1.0,
            correlation_id=context.get("correlation_id", "golden"),
        )


@dataclass(frozen=True)
class AgentResponse:
    change: ChangeEvent
    plan: RepairPlan
    spoken_summary: str
    requires_approval: bool


class RippleAgent:
    """Intelligence facade: interpret a natural-language change, then plan safely.

    Important: the interpreter/model never executes tools. Writes remain behind
    ApprovalPolicy + Executor.
    """
    def __init__(self, interpreter: ChangeInterpreter, planner: Planner):
        self.interpreter = interpreter
        self.planner = planner

    def propose(self, utterance: str, context: Dict[str, Any]) -> AgentResponse:
        change = self.interpreter.interpret(utterance, context)
        plan = self.planner.build_plan(change)
        money = (
            f"The plan adds ${plan.total_added_cost:.0f}, avoids up to "
            f"${plan.total_avoidable_loss:.0f} in direct loss, and preserves "
            f"${plan.net_direct_cash_preserved:.0f} net."
        )
        people = (
            f" It will notify {plan.external_people_notified} external people."
            if plan.external_people_notified else ""
        )
        spoken = (
            f"I found {len(plan.impacts)} downstream commitments to repair. "
            f"{money}{people} I need your approval before I change anything."
        )
        return AgentResponse(change, plan, spoken, requires_approval=True)
