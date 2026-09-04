import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from ripple.golden import run_golden


def test_golden_contract():
    plan, first, second, tools = run_golden()
    assert len(plan.impacts) == 5
    assert plan.total_added_cost == 42
    assert plan.total_avoidable_loss == 116
    assert plan.net_direct_cash_preserved == 74
    assert plan.external_people_notified == 3
    assert len(plan.actions) == 5
    assert sum(r.status == "executed" for r in first) == 5
    assert sum(r.status == "deduplicated" for r in second) == 5
    assert len(tools.execution_log) == 5
    assert len(first) == 5 and len(second) == 5
