# Ripple — AWS Ready Gate v1.5

**Overall: PASS**

| Check | Result |
|---|---|
| `dynamodb_on_demand` | PASS |
| `dynamodb_pitr` | PASS |
| `application_inference_profile` | PASS |
| `runtime_policy_no_resource_star` | PASS |
| `bedrock_inference_profile_condition` | PASS |
| `cloudwatch_bounded_retention` | PASS |
| `budget_account_wide_no_tag_activation_dependency` | PASS |
| `budget_monthly_cost_guard` | PASS |
| `budget_thresholds` | PASS |
| `normalizer_fixture_count` | PASS |

Bedrock normalization benchmark fixtures: **5**

The budget check intentionally requires an account-wide guard with no cost-allocation-tag activation dependency.

This gate proves deployable configuration and local contracts only. It does not claim that an AWS stack has been created or that either Nova model has been invoked live.
