from ripple.evaluation.cost_benchmark import (
    NOVA_2_LITE,
    NOVA_LITE,
    model_cost,
    railway_idle_cost,
)


def test_model_planning_envelope_is_exact_and_quality_policy_stays_separate():
    nova_lite = model_cost(NOVA_LITE)
    nova_2_lite = model_cost(NOVA_2_LITE)

    assert round(nova_lite.cost_per_change_usd, 8) == 0.00018144
    assert round(nova_lite.cost_10k_changes_usd, 4) == 1.8144
    assert round(nova_2_lite.cost_per_change_usd, 8) == 0.00124
    assert round(nova_2_lite.cost_10k_changes_usd, 2) == 12.40
    assert nova_lite.cost_per_change_usd < nova_2_lite.cost_per_change_usd


def test_railway_idle_envelope_is_below_hobby_billing_floor():
    row = railway_idle_cost()
    assert round(row.modeled_monthly_usd, 6) == 0.257673
    assert row.billing_floor_usd == 5.0
    assert row.effective_monthly_floor_usd == 5.0
