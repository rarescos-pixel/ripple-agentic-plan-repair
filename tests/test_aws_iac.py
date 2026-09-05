import json
from pathlib import Path


TEMPLATE = Path(__file__).resolve().parents[1] / "infra" / "ripple-aws.json"


def load_template():
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


def test_dynamodb_is_on_demand_encrypted_and_has_short_pitr_window():
    t = load_template()
    p = t["Resources"]["StateTable"]["Properties"]
    assert p["BillingMode"] == "PAY_PER_REQUEST"
    assert p["SSESpecification"]["SSEEnabled"] is True
    assert p["PointInTimeRecoverySpecification"] == {
        "PointInTimeRecoveryEnabled": True,
        "RecoveryPeriodInDays": 7,
    }


def test_bedrock_uses_tagged_application_inference_profile():
    t = load_template()
    p = t["Resources"]["RippleInferenceProfile"]
    assert p["Type"] == "AWS::Bedrock::ApplicationInferenceProfile"
    tags = p["Properties"]["Tags"]
    assert any(tag["Key"] == "Project" for tag in tags)
    assert "BedrockApplicationInferenceProfileArn" in t["Outputs"]


def test_runtime_policy_has_no_unbounded_resource_star():
    t = load_template()
    statements = t["Resources"]["RuntimePolicy"]["Properties"]["PolicyDocument"]["Statement"]
    assert all(s["Effect"] == "Allow" for s in statements)
    assert all(s["Resource"] != "*" for s in statements)
    actions = {a for s in statements for a in s["Action"]}
    assert actions == {
        "dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DescribeTable",
        "logs:PutLogEvents", "bedrock:InvokeModel",
    }
    bedrock_models = next(s for s in statements if s["Sid"] == "RippleBedrockUnderlyingModels")
    assert "bedrock:InferenceProfileArn" in bedrock_models["Condition"]["StringEquals"]


def test_budget_is_account_wide_and_alerts_at_50_80_100_percent():
    t = load_template()
    b = t["Resources"]["RippleBudget"]["Properties"]
    budget = b["Budget"]
    # A new AWS account cannot rely on a user-defined cost-allocation tag being
    # activated before the live gate. The safety budget therefore covers the
    # whole account; Project tags remain on resources for later attribution.
    assert "CostFilters" not in budget
    assert budget["BudgetType"] == "COST"
    assert budget["TimeUnit"] == "MONTHLY"
    assert budget["BudgetLimit"] == {"Amount": {"Ref": "MonthlyBudgetUSD"}, "Unit": "USD"}
    thresholds = [x["Notification"]["Threshold"] for x in b["NotificationsWithSubscribers"]]
    assert thresholds == [50, 80, 100]
    assert all(x["Notification"]["NotificationType"] == "ACTUAL" for x in b["NotificationsWithSubscribers"])


def test_cloudwatch_retention_is_bounded():
    t = load_template()
    assert t["Resources"]["TraceLogGroup"]["Properties"]["RetentionInDays"] == 14
