#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-eu-central-1}"
STACK_NAME="${RIPPLE_AWS_STACK_NAME:-ripple-demo}"
MONTHLY_BUDGET_USD="${RIPPLE_MONTHLY_BUDGET_USD:-10}"
REPO_URL="https://github.com/rarescos-pixel/ripple-agentic-plan-repair.git"
SOURCE_REF="${RIPPLE_SOURCE_REF:-main}"

for cmd in aws git python3; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "Missing required command: $cmd" >&2; exit 2; }
done

IDENTITY_JSON="$(aws sts get-caller-identity --output json)"
ACCOUNT_ID="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["Account"])' <<<"$IDENTITY_JSON")"
CALLER_ARN="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["Arn"])' <<<"$IDENTITY_JSON")"

echo "AWS authenticated: account ****${ACCOUNT_ID: -4}"
echo "Caller: $CALLER_ARN"
echo "Region: $AWS_REGION"

if [[ -z "${RIPPLE_BUDGET_EMAIL:-}" ]]; then
  read -r -p "Email for AWS Budget alerts: " RIPPLE_BUDGET_EMAIL
fi
if [[ -z "$RIPPLE_BUDGET_EMAIL" || "$RIPPLE_BUDGET_EMAIL" != *@*.* ]]; then
  echo "A valid budget alert email is required." >&2
  exit 2
fi

WORKDIR="$(mktemp -d -t ripple-aws-live-XXXXXX)"
trap 'rm -rf "$WORKDIR"' EXIT

echo "Cloning Ripple source..."
git clone --quiet --depth 1 --branch "$SOURCE_REF" "$REPO_URL" "$WORKDIR/repo"
cd "$WORKDIR/repo"
SOURCE_SHA="$(git rev-parse HEAD)"
echo "Source SHA: $SOURCE_SHA"

python3 -m pip install --user --quiet -e '.[aws]'

# Quality first: benchmark both supported Nova options before creating the Application Inference Profile.
echo "Running live Nova Lite vs Nova 2 Lite normalization benchmark..."
python3 scripts/bedrock_benchmark.py \
  --region "$AWS_REGION" \
  --json-output "$WORKDIR/bedrock-benchmark.json" \
  --output "$WORKDIR/BEDROCK_BENCHMARK_LIVE.md" \
  --require-perfect | tee "$WORKDIR/bedrock-benchmark.log"

WINNER="$(grep '^RIPPLE_BEDROCK_RECOMMENDED=' "$WORKDIR/bedrock-benchmark.log" | tail -n1 | cut -d= -f2-)"
if [[ -z "$WINNER" ]]; then
  echo "Could not determine a benchmark winner." >&2
  exit 3
fi

echo "Selected Bedrock geo profile: $WINNER"

# Deploy the real, cost-scoped stack using the model that won the live benchmark.
export RIPPLE_BUDGET_EMAIL
export RIPPLE_MONTHLY_BUDGET_USD="$MONTHLY_BUDGET_USD"
export RIPPLE_BEDROCK_GEO_PROFILE_ID="$WINNER"
export RIPPLE_AWS_STACK_NAME="$STACK_NAME"
export AWS_REGION

bash scripts/aws_deploy.sh

OUTPUTS_FILE="$WORKDIR/stack-outputs.json"
aws cloudformation describe-stacks \
  --region "$AWS_REGION" \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs' \
  --output json > "$OUTPUTS_FILE"

output_value() {
  local key="$1"
  python3 -c '
import json, sys
key, path = sys.argv[1], sys.argv[2]
with open(path, "r", encoding="utf-8") as f:
    items = json.load(f)
for item in items:
    if item.get("OutputKey") == key:
        print(item.get("OutputValue", ""))
        raise SystemExit(0)
raise SystemExit(f"Missing CloudFormation output: {key}")
' "$key" "$OUTPUTS_FILE"
}

TABLE="$(output_value StateTableName)"
LOG_GROUP="$(output_value TraceLogGroupName)"
LOG_STREAM="$(output_value TraceLogStreamName)"
PROFILE_ARN="$(output_value BedrockApplicationInferenceProfileArn)"
POLICY_ARN="$(output_value RuntimePolicyArn)"

# Exercise the actual deployed resources through Ripple's production adapters.
echo "Running live DynamoDB + CloudWatch + Application Inference Profile verification..."
python3 scripts/aws_live_verify.py \
  --region "$AWS_REGION" \
  --table "$TABLE" \
  --log-group "$LOG_GROUP" \
  --log-stream "$LOG_STREAM" \
  --profile-arn "$PROFILE_ARN" \
  --budget-name "ripple-demo-monthly" | tee "$WORKDIR/aws-live-verify.log"

# Only after the AWS stack itself has passed live verification, prepare the
# tightly-scoped external-runtime credential bundle. The secret is written to a
# 0600 file in the authenticated CloudShell home directory and is never echoed.
echo "Preparing least-privilege Railway runtime credential bundle..."
bash scripts/aws_railway_runtime_principal.sh

cat <<EOF

RIPPLE_AWS_LIVE_HANDOFF_BEGIN
status=PASS
source_sha=$SOURCE_SHA
region=$AWS_REGION
stack_name=$STACK_NAME
selected_bedrock_geo_profile=$WINNER
state_table=$TABLE
trace_log_group=$LOG_GROUP
trace_log_stream=$LOG_STREAM
application_inference_profile_arn=$PROFILE_ARN
runtime_policy_arn=$POLICY_ARN
monthly_budget_usd=$MONTHLY_BUDGET_USD
aws_account_suffix=${ACCOUNT_ID: -4}
runtime_principal_prepared=true
RIPPLE_AWS_LIVE_HANDOFF_END

AWS resources are live-verified and the least-privilege Railway runtime bundle is prepared.
Do NOT print, commit, email, or paste the credential bundle or AWS secret values into ChatGPT.
Only the RIPPLE_AWS_LIVE_VERIFY_* / RIPPLE_AWS_LIVE_HANDOFF_* / RIPPLE_AWS_RAILWAY_PRINCIPAL_* non-secret blocks are safe to share.
EOF
