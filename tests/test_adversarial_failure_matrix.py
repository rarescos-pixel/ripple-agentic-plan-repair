from ripple.evaluation.adversarial import run_adversarial_matrix


def test_adversarial_failure_matrix_all_invariants_pass():
    rows = run_adversarial_matrix()
    assert len(rows) == 8
    assert all(row.passed for row in rows), [row.scenario for row in rows if not row.passed]

    by_name = {row.scenario: row for row in rows}
    assert by_name["approval_cost_cap"].observed["writes"] == 0
    assert by_name["approval_people_cap"].observed["writes"] == 0
    assert by_name["wrong_plan_version"].observed["writes"] == 0
    assert by_name["ambiguous_provider"].observed["writes"] == 0
    assert by_name["provider_partial_failure"].observed["plan_status"] == "partial"
    assert by_name["interruption_recovery"].observed["unique_writes_total"] == 5
    assert by_name["interruption_recovery"].observed["deduplicated_on_resume"] == 2
