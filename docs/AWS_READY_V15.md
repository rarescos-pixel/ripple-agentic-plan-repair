# Ripple v1.5 — AWS-ready activation plan

## Scope

Ripple keeps the public MCP/OAuth service on Railway. AWS augments only the capabilities that materially improve the Alexa+ submission:

- **Amazon Bedrock** — normalize one user-reported changed fact; never choose repairs or execute tools.
- **Amazon DynamoDB** — persist exact approvals and authoritative idempotency receipts across process restarts.
- **Amazon CloudWatch Logs** — structured, redacted judge/debug traces.
- **AWS Budgets** — project-tag-scoped spend alerts.
- **IAM managed policy** — only DynamoDB state, one CloudWatch stream, and Bedrock invocation through the Ripple inference profile.

No ECS/Fargate duplication is introduced. Railway remains the MCP transport host.

## Infrastructure

`infra/ripple-aws.json` creates:

1. `StateTable` — DynamoDB `PAY_PER_REQUEST`, SSE enabled, 7-day PITR.
2. `TraceLogGroup` + `TraceLogStream` — 14-day retention.
3. `RippleInferenceProfile` — tagged Bedrock Application Inference Profile copied from the selected EU geographic inference profile.
4. `RuntimePolicy` — managed least-privilege policy for the external runtime principal.
5. `RippleBudget` — monthly budget alerts at 50%, 80%, and 100%, filtered on `Project=Ripple`.

The default Bedrock source is `eu.amazon.nova-2-lite-v1:0`. The benchmark can compare it with `eu.amazon.nova-lite-v1:0` before the final model is locked.

## Deploy

Prerequisites: AWS CLI authenticated to the intended account, permissions to create the declared resources, Bedrock model access, and a budget-alert email.

```bash
export AWS_REGION=eu-central-1
export RIPPLE_BUDGET_EMAIL='<your-alert-email>'
export RIPPLE_MONTHLY_BUDGET_USD=10
bash scripts/aws_deploy.sh
```

Before relying on the tag-scoped budget, activate the user-defined `Project` cost allocation tag in AWS Billing. AWS Budgets alerts are notifications, not a guaranteed service shutdown.

## Railway runtime mapping

After stack creation, attach the `RuntimePolicyArn` output to the AWS principal used by Railway and configure:

```text
AWS_REGION=eu-central-1
RIPPLE_STATE_BACKEND=dynamodb
RIPPLE_DYNAMODB_TABLE=<StateTableName>
RIPPLE_CHANGE_INTERPRETER=bedrock
RIPPLE_BEDROCK_MODEL_ID=<BedrockApplicationInferenceProfileArn>
RIPPLE_TRACE_BACKEND=cloudwatch
RIPPLE_CLOUDWATCH_LOG_GROUP=<TraceLogGroupName>
RIPPLE_CLOUDWATCH_LOG_STREAM=runtime
```

AWS credentials must remain in Railway/AWS secret storage and must never be committed.

## Bedrock trust boundary

The model receives only canonical node IDs, mutable fields and the user's change utterance. It must call `record_change` exactly once. Ripple rejects:

- non-canonical node IDs;
- non-whitelisted fields;
- missing/invalid values;
- confidence below the configured threshold;
- zero or multiple tool calls.

The authoritative old value always comes from application state. Bedrock cannot approve, rank financial repair actions, or execute provider writes.

## CloudWatch trace boundary

Trace schema: `ripple.trace.v1`.

Emitted runtime events:

- `change.recorded`
- `plan.previewed`
- `plan.approved`
- `plan.executed`

The trace sink recursively redacts authorization, password, secret, token, cookie and API-key fields. It does not log the raw user utterance. Message size is bounded before `PutLogEvents`.

## Bedrock benchmark

Install AWS extras, then run real inference:

```bash
python -m pip install -e '.[aws]'
python scripts/bedrock_benchmark.py --region eu-central-1
```

The benchmark uses five canonical normalization cases and ranks models by:

1. exact normalization accuracy;
2. total token volume when quality ties;
3. median latency when quality and token volume tie.

No model-quality conclusion is accepted from fake-client CI. The live report `docs/BEDROCK_BENCHMARK_LIVE.md` should be committed only after real Bedrock calls.

## Required live evidence before claiming AWS Builder integration

A live AWS pass must prove all of the following on one source SHA:

- CloudFormation stack `CREATE_COMPLETE`/`UPDATE_COMPLETE`;
- Application Inference Profile active and tagged `Project=Ripple`;
- real Bedrock `Converse` normalization succeeds through the application profile;
- DynamoDB approval survives a new process/session;
- DynamoDB authoritative receipt suppresses replay duplication;
- CloudWatch receives redacted `ripple.trace.v1` events;
- budget exists with 50/80/100% alert thresholds;
- Railway public MCP smoke remains PASS after AWS activation;
- no AWS credentials appear in logs, repo, reports, or screenshots.

Until those checks are captured, v1.5 is **AWS-ready**, not **AWS-live verified**.

## Teardown

```bash
bash scripts/aws_teardown.sh
```

Teardown is part of the cost-control plan. Do not delete the stack while judging still depends on AWS-backed evidence/runtime.
