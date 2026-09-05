#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import boto3

from ripple.aws.bedrock import TrackedBedrockConverseClient
from ripple.domain.models import Approval, ExecutionReceipt
from ripple.evaluation.bedrock_benchmark import load_cases
from ripple.observability.cloudwatch import CloudWatchTraceSink
from ripple.orchestration.bedrock_interpreter import BedrockChangeInterpreter
from ripple.persistence.store import DynamoDbStateStore


def main() -> None:
    p = argparse.ArgumentParser(description="Verify Ripple against live AWS resources without exposing credentials.")
    p.add_argument("--region", required=True)
    p.add_argument("--table", required=True)
    p.add_argument("--log-group", required=True)
    p.add_argument("--log-stream", default="runtime")
    p.add_argument("--profile-arn", required=True)
    p.add_argument("--budget-name", default="ripple-demo-monthly")
    p.add_argument("--cases", default="fixtures/bedrock_normalization_cases.json")
    args = p.parse_args()

    sts = boto3.client("sts", region_name=args.region)
    identity = sts.get_caller_identity()
    account_id = identity["Account"]

    # 1) DynamoDB: real durable approval + atomic authoritative receipt semantics.
    store = DynamoDbStateStore(args.table, region_name=args.region)
    stamp = str(int(time.time()))
    plan_id = f"live-verify-{stamp}"
    snapshot = f"live-snapshot-{stamp}"
    approval = Approval(
        plan_id=plan_id,
        plan_version=1,
        max_total_cost=42,
        external_people_notified=3,
        plan_snapshot_hash=snapshot,
        actor="aws-live-verifier",
    )
    store.save_approval(plan_id, approval)
    loaded_approval = store.get_approval(plan_id, snapshot)
    if loaded_approval != approval:
        raise RuntimeError("DynamoDB approval read-after-write mismatch")

    key = f"live-idempotency-{stamp}"
    executed = ExecutionReceipt(
        action_id="live-action",
        idempotency_key=key,
        status="executed",
        result={"provider": "live-verification", "ok": True},
        attempt=1,
    )
    store.save_receipt(plan_id, executed)
    # A later conflicting receipt must not overwrite the authoritative executed receipt.
    store.save_receipt(
        plan_id,
        ExecutionReceipt(
            action_id="live-action",
            idempotency_key=key,
            status="failed",
            result={"provider": "should-not-win"},
            attempt=2,
        ),
    )
    loaded_receipt = store.get_receipt(key)
    if loaded_receipt is None or loaded_receipt.status != "executed" or loaded_receipt.result.get("ok") is not True:
        raise RuntimeError("DynamoDB conditional receipt invariant failed")

    # 2) CloudWatch Logs: emit a real trace and verify secret redaction in the stored event.
    logs = boto3.client("logs", region_name=args.region)
    sink = CloudWatchTraceSink(logs, args.log_group, args.log_stream)
    secret_probe = f"never-store-{stamp}"
    correlation_id = f"aws-live-{stamp}"
    sink.emit(
        "aws.live.verify",
        correlation_id=correlation_id,
        payload={"safe": "ok", "password": secret_probe, "access_token": secret_probe},
    )
    time.sleep(1.0)
    events = logs.get_log_events(
        logGroupName=args.log_group,
        logStreamName=args.log_stream,
        startFromHead=False,
        limit=50,
    ).get("events", [])
    matching = [e.get("message", "") for e in events if correlation_id in e.get("message", "")]
    if not matching:
        raise RuntimeError("CloudWatch verification event was not readable after write")
    stored_message = matching[-1]
    if secret_probe in stored_message or "[REDACTED]" not in stored_message:
        raise RuntimeError("CloudWatch secret-redaction invariant failed")

    # 3) Bedrock: invoke the actual Application Inference Profile through Converse/tool-use.
    cases = load_cases(args.cases)
    if not cases:
        raise RuntimeError("No Bedrock benchmark fixtures available")
    case = cases[0]
    bedrock_client = TrackedBedrockConverseClient(region_name=args.region)
    interpreter = BedrockChangeInterpreter(client=bedrock_client, model_id=args.profile_arn)
    change = interpreter.interpret(case.utterance, dict(case.context))
    observed = {"node_id": change.node_id, "field": change.field, "new_value": change.new_value}
    if observed != case.expected:
        raise RuntimeError(f"Application Inference Profile normalization mismatch: {observed!r} != {case.expected!r}")

    # 4) Budget exists and is an effective account-wide guard. User-defined tag
    # filters require cost-allocation-tag activation and can take up to 24h to
    # become usable on a new account, so the live safety budget intentionally
    # has no CostFilters dependency.
    budgets = boto3.client("budgets", region_name="us-east-1")
    budget = budgets.describe_budget(AccountId=account_id, BudgetName=args.budget_name)["Budget"]
    if budget.get("BudgetType") != "COST" or budget.get("TimeUnit") != "MONTHLY":
        raise RuntimeError("AWS Budget is not the expected monthly COST guard")
    if budget.get("CostFilters"):
        raise RuntimeError("AWS Budget unexpectedly depends on cost filters/tag activation")
    limit = budget.get("BudgetLimit") or {}
    if limit.get("Unit") != "USD" or float(limit.get("Amount", 0)) <= 0:
        raise RuntimeError("AWS Budget has no positive USD limit")

    result = {
        "status": "PASS",
        "region": args.region,
        "account_suffix": account_id[-4:],
        "dynamodb": {
            "table": args.table,
            "approval_roundtrip": True,
            "authoritative_receipt_preserved": True,
        },
        "cloudwatch": {
            "log_group": args.log_group,
            "log_stream": args.log_stream,
            "trace_written": True,
            "secret_redaction_verified": True,
            "correlation_id": correlation_id,
        },
        "bedrock": {
            "application_profile_arn": args.profile_arn,
            "converse_tool_use_verified": True,
            "fixture": case.id,
            "usage": dict(getattr(bedrock_client, "last_usage", {}) or {}),
        },
        "budget": {
            "name": budget.get("BudgetName"),
            "limit": limit,
            "scope": "account-wide",
            "cost_filters": budget.get("CostFilters") or {},
            "tag_activation_dependency": False,
        },
    }
    print("RIPPLE_AWS_LIVE_VERIFY_BEGIN")
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    print("RIPPLE_AWS_LIVE_VERIFY_END")


if __name__ == "__main__":
    main()
