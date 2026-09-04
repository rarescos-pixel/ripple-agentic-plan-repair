# AWS durable state target

Ripple's production durability target is a single DynamoDB table used only for safety-critical orchestration state: exact approvals and authoritative execution receipts.

## Item model

Approval:

```text
pk = PLAN#<plan_id>
sk = APPROVAL#<snapshot_hash>
entity_type = approval
payload = canonical JSON Approval
```

Receipt:

```text
pk = IDEMPOTENCY#<idempotency_key>
sk = RECEIPT
entity_type = receipt
plan_id = <plan_id>
payload = canonical JSON ExecutionReceipt
```

The lookup pattern is intentionally narrow: approval by exact plan+snapshot and receipt by idempotency key. No scans are required for the execution safety path.

## Least-privilege application permissions

The Ripple runtime needs only:

```text
dynamodb:GetItem
dynamodb:PutItem
```

on the single Ripple state table for this MVP contract. Table creation, deletion, backups and IAM administration belong to deployment roles, not the application role.

## Cost posture

Use DynamoDB on-demand billing for the hackathon and early product stage. Ripple writes one approval plus at most one authoritative receipt per repair action and reads an idempotency key before each action. The storage and request volume are tiny compared with the economic value of the disruptions Ripple is designed to mitigate.

## Live-AWS gate

The adapter exists and is covered by deterministic client-injection tests. A live AWS table, CloudWatch evidence and an AWS account cost/budget alarm are still external deployment gates and must not be claimed until actually provisioned and exercised.
