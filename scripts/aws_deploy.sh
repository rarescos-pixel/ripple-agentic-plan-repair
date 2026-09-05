#!/usr/bin/env bash
set -euo pipefail

: "${RIPPLE_BUDGET_EMAIL:?Set RIPPLE_BUDGET_EMAIL before deployment}"
AWS_REGION="${AWS_REGION:-eu-central-1}"
STACK_NAME="${RIPPLE_AWS_STACK_NAME:-ripple-demo}"
MONTHLY_BUDGET_USD="${RIPPLE_MONTHLY_BUDGET_USD:-10}"
BEDROCK_GEO_PROFILE_ID="${RIPPLE_BEDROCK_GEO_PROFILE_ID:-eu.amazon.nova-2-lite-v1:0}"

aws cloudformation validate-template \
  --region "$AWS_REGION" \
  --template-body file://infra/ripple-aws.json >/dev/null

aws cloudformation deploy \
  --region "$AWS_REGION" \
  --stack-name "$STACK_NAME" \
  --template-file infra/ripple-aws.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    EnvironmentName=demo \
    BudgetEmail="$RIPPLE_BUDGET_EMAIL" \
    MonthlyBudgetUSD="$MONTHLY_BUDGET_USD" \
    BedrockGeoProfileId="$BEDROCK_GEO_PROFILE_ID" \
    ProjectTagValue=Ripple \
  --tags Project=Ripple Environment=demo

aws cloudformation describe-stacks \
  --region "$AWS_REGION" \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs' \
  --output table

cat <<'EOF'

Next: attach RuntimePolicyArn to the AWS principal used by Railway, then set:
  RIPPLE_STATE_BACKEND=dynamodb
  RIPPLE_DYNAMODB_TABLE=<StateTableName output>
  RIPPLE_CHANGE_INTERPRETER=bedrock
  RIPPLE_BEDROCK_MODEL_ID=<BedrockApplicationInferenceProfileArn output>
  RIPPLE_TRACE_BACKEND=cloudwatch
  RIPPLE_CLOUDWATCH_LOG_GROUP=<TraceLogGroupName output>
  RIPPLE_CLOUDWATCH_LOG_STREAM=runtime
  AWS_REGION=eu-central-1

Do not store AWS credentials in the repository. The monthly AWS Budget is intentionally account-wide, so no cost-allocation-tag activation is required before relying on the spend guard.
EOF
