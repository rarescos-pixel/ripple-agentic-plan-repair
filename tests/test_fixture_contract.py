import json
from pathlib import Path

from ripple.webapp import DemoController


def test_human_readable_golden_fixture_matches_executable_contract():
    fixture = json.loads((Path(__file__).parents[1] / "fixtures" / "golden_scenario.json").read_text())
    c = DemoController()
    proposal = c.propose(fixture["utterance"])
    expected = fixture["expected"]
    assert proposal["plan"]["impact_count"] == expected["impact_count"]
    assert proposal["plan"]["action_count"] == expected["action_count"]
    assert proposal["plan"]["total_added_cost"] == expected["added_cost"]
    assert proposal["plan"]["total_avoidable_loss"] == expected["direct_avoidable_loss"]
    assert proposal["plan"]["net_direct_cash_preserved"] == expected["net_direct_cash_preserved"]
    assert proposal["plan"]["external_people_notified"] == expected["external_people_notified"]
    assert proposal["writes_before_approval"] == expected["writes_before_approval"]
    executed = c.approve(proposal["approval_disclosure"])
    assert executed["external_write_count"] == expected["unique_external_writes_after_execution"]
    replay = c.replay()
    assert replay["deduplicated"] == expected["deduplicated_actions_on_replay"]
