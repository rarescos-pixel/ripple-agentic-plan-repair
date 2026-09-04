from ripple.evaluation.release_gate import collect_release_evidence


def test_release_gate_is_green_and_quantified():
    evidence = collect_release_evidence()
    assert evidence["passed"] is True
    assert all(evidence["checks"].values())
    assert evidence["golden"]["impacts"] == 5
    assert evidence["golden"]["writes_before_approval"] == 0
    assert evidence["golden"]["replay_deduplicated"] == 5
    assert len(evidence["scenario_matrix"]) == 7
