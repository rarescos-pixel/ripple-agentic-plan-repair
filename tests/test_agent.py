import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from ripple.golden import build_golden
from ripple.orchestration.agent import GoldenChangeInterpreter, RippleAgent
from ripple.orchestration.session import RippleSession


def build_session():
    _, tools, planner, executor, _ = build_golden()
    agent = RippleAgent(GoldenChangeInterpreter(), planner)
    return RippleSession(agent, executor), tools


def context():
    return {"old_arrival_at":"2026-09-10T21:00:00", "new_arrival_at":"2026-09-11T18:00:00"}


def test_natural_language_produces_locked_golden_plan():
    session, tools = build_session()
    p = session.propose("Our flight home was cancelled. We'll land tomorrow at 18:00.", context())
    assert p.requires_approval is True
    assert len(p.plan.impacts) == 5
    assert p.plan.total_added_cost == 42
    assert p.plan.total_avoidable_loss == 116
    assert "5 downstream commitments" in p.spoken_summary
    assert len(tools.execution_log) == 0  # proposal phase has no writes


def test_execution_only_happens_after_exact_approval():
    session, tools = build_session()
    p = session.propose("Our flight home was cancelled. We'll land tomorrow at 18:00.", context())
    assert len(tools.execution_log) == 0
    r = session.approve_and_execute(p, max_total_cost=42, external_people_notified=3)
    assert sum(x.status == "executed" for x in r.receipts) == 5
    assert len(tools.execution_log) == 5


def test_interpreter_rejects_out_of_contract_intent():
    session, _ = build_session()
    with pytest.raises(ValueError, match="outside the v0.3 golden interpreter contract"):
        session.propose("Book me a restaurant for Friday", context())
