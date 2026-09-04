from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = ROOT / "infra" / "ripple-aws.json"
CASES = ROOT / "fixtures" / "bedrock_normalization_cases.json"


def collect() -> dict[str, Any]:
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    resources = template["Resources"]
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    statements = resources["RuntimePolicy"]["Properties"]["PolicyDocument"]["Statement"]
    thresholds = [
        n["Notification"]["Threshold"]
        for n in resources["RippleBudget"]["Properties"]["NotificationsWithSubscribers"]
    ]
    checks = {
        "dynamodb_on_demand": resources["StateTable"]["Properties"]["BillingMode"] == "PAY_PER_REQUEST",
        "dynamodb_pitr": resources["StateTable"]["Properties"]["PointInTimeRecoverySpecification"]["PointInTimeRecoveryEnabled"] is True,
        "application_inference_profile": resources["RippleInferenceProfile"]["Type"] == "AWS::Bedrock::ApplicationInferenceProfile",
        "runtime_policy_no_resource_star": all(s["Resource"] != "*" for s in statements),
        "bedrock_inference_profile_condition": any(
            "bedrock:InferenceProfileArn" in s.get("Condition", {}).get("StringEquals", {})
            for s in statements
        ),
        "cloudwatch_bounded_retention": resources["TraceLogGroup"]["Properties"]["RetentionInDays"] == 14,
        "budget_project_tag_filter": "TagKeyValue" in resources["RippleBudget"]["Properties"]["Budget"]["CostFilters"],
        "budget_thresholds": thresholds == [50, 80, 100],
        "normalizer_fixture_count": len(cases) >= 5,
    }
    return {"passed": all(checks.values()), "checks": checks, "fixture_count": len(cases)}


def render(evidence: dict[str, Any]) -> str:
    lines = [
        "# Ripple — AWS Ready Gate v1.5",
        "",
        f"**Overall: {'PASS' if evidence['passed'] else 'FAIL'}**",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    lines += [f"| `{name}` | {'PASS' if passed else 'FAIL'} |" for name, passed in evidence["checks"].items()]
    lines += [
        "",
        f"Bedrock normalization benchmark fixtures: **{evidence['fixture_count']}**",
        "",
        "This gate proves deployable configuration and local contracts only. It does not claim that an AWS stack has been created or that either Nova model has been invoked live.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    evidence = collect()
    report = render(evidence)
    (ROOT / "docs" / "AWS_READY_REPORT.md").write_text(report, encoding="utf-8")
    print(report)
    if not evidence["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
