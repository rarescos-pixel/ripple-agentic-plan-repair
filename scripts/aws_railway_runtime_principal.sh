#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-eu-central-1}"
STACK_NAME="${RIPPLE_AWS_STACK_NAME:-ripple-demo}"
IAM_USER="${RIPPLE_RUNTIME_IAM_USER:-ripple-railway-runtime}"
CREDENTIAL_FILE="${RIPPLE_RUNTIME_CREDENTIAL_FILE:-$HOME/.ripple/railway-aws.env}"

for cmd in aws python3; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "Missing required command: $cmd" >&2; exit 2; }
done

OUTPUTS_JSON="$(aws cloudformation describe-stacks \
  --region "$AWS_REGION" \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs' \
  --output json)"

output_value() {
  local key="$1"
  python3 -c '
import json, sys
key = sys.argv[1]
for item in json.load(sys.stdin):
    if item.get("OutputKey") == key:
        print(item.get("OutputValue", ""))
        raise SystemExit(0)
raise SystemExit(f"Missing CloudFormation output: {key}")
' "$key" <<<"$OUTPUTS_JSON"
}

TABLE="$(output_value StateTableName)"
LOG_GROUP="$(output_value TraceLogGroupName)"
LOG_STREAM="$(output_value TraceLogStreamName)"
PROFILE_ARN="$(output_value BedrockApplicationInferenceProfileArn)"
POLICY_ARN="$(output_value RuntimePolicyArn)"

if ! aws iam get-user --user-name "$IAM_USER" >/dev/null 2>&1; then
  aws iam create-user \
    --user-name "$IAM_USER" \
    --tags Key=Project,Value=Ripple Key=Environment,Value=demo Key=Purpose,Value=RailwayRuntime >/dev/null
fi

# This principal is dedicated to Ripple. Remove any stale attached policy before
# attaching the current stack policy so its effective permissions cannot grow
# across a stack recreation.
ATTACHED_POLICIES="$(aws iam list-attached-user-policies \
  --user-name "$IAM_USER" \
  --query 'AttachedPolicies[].PolicyArn' \
  --output text)"
for attached in $ATTACHED_POLICIES; do
  if [[ "$attached" != "$POLICY_ARN" ]]; then
    aws iam detach-user-policy --user-name "$IAM_USER" --policy-arn "$attached"
  fi
done
aws iam attach-user-policy --user-name "$IAM_USER" --policy-arn "$POLICY_ARN"

ACTIVE_KEYS="$(aws iam list-access-keys \
  --user-name "$IAM_USER" \
  --query 'AccessKeyMetadata[?Status==`Active`].AccessKeyId' \
  --output text)"
read -r -a ACTIVE_KEY_ARRAY <<<"$ACTIVE_KEYS"

if (( ${#ACTIVE_KEY_ARRAY[@]} > 1 )); then
  echo "Refusing ambiguous credential state: $IAM_USER has more than one active access key." >&2
  exit 4
fi

if (( ${#ACTIVE_KEY_ARRAY[@]} == 1 )); then
  ACCESS_KEY_ID="${ACTIVE_KEY_ARRAY[0]}"
  if [[ ! -f "$CREDENTIAL_FILE" ]]; then
    echo "Refusing to rotate implicitly: an active key exists but the private credential bundle is missing." >&2
    exit 4
  fi
  BUNDLE_ACCESS_KEY_ID="$(python3 -c '
import pathlib, sys
values = {}
for line in pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    if "=" in line:
        key, value = line.split("=", 1)
        values[key] = value
print(values.get("AWS_ACCESS_KEY_ID", ""))
' "$CREDENTIAL_FILE")"
  if [[ "$BUNDLE_ACCESS_KEY_ID" != "$ACCESS_KEY_ID" ]]; then
    echo "Refusing to rotate implicitly: active AWS key does not match the private credential bundle." >&2
    exit 4
  fi

  # Reconcile non-secret runtime outputs after a stack update/recreation while
  # preserving the existing private key material entirely inside the 0600 file.
  python3 -c '
import pathlib, sys
out = pathlib.Path(sys.argv[1]).expanduser()
region, table, profile_arn, log_group, log_stream = sys.argv[2:]
values = {}
for line in out.read_text(encoding="utf-8").splitlines():
    if "=" in line:
        key, value = line.split("=", 1)
        values[key] = value
if not values.get("AWS_ACCESS_KEY_ID") or not values.get("AWS_SECRET_ACCESS_KEY"):
    raise SystemExit("Credential bundle is incomplete")
values.update({
    "AWS_REGION": region,
    "RIPPLE_STATE_BACKEND": "dynamodb",
    "RIPPLE_DYNAMODB_TABLE": table,
    "RIPPLE_CHANGE_INTERPRETER": "bedrock",
    "RIPPLE_BEDROCK_MODEL_ID": profile_arn,
    "RIPPLE_TRACE_BACKEND": "cloudwatch",
    "RIPPLE_CLOUDWATCH_LOG_GROUP": log_group,
    "RIPPLE_CLOUDWATCH_LOG_STREAM": log_stream,
    "RIPPLE_REQUIRE_AWS_RUNTIME": "true",
})
order = [
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION",
    "RIPPLE_STATE_BACKEND", "RIPPLE_DYNAMODB_TABLE",
    "RIPPLE_CHANGE_INTERPRETER", "RIPPLE_BEDROCK_MODEL_ID",
    "RIPPLE_TRACE_BACKEND", "RIPPLE_CLOUDWATCH_LOG_GROUP",
    "RIPPLE_CLOUDWATCH_LOG_STREAM", "RIPPLE_REQUIRE_AWS_RUNTIME",
]
out.write_text("".join(f"{name}={values[name]}\n" for name in order), encoding="utf-8")
out.chmod(0o600)
' "$CREDENTIAL_FILE" "$AWS_REGION" "$TABLE" "$PROFILE_ARN" "$LOG_GROUP" "$LOG_STREAM"

  cat <<EOF
RIPPLE_AWS_RAILWAY_PRINCIPAL_BEGIN
status=REUSED
iam_user=$IAM_USER
runtime_policy_arn=$POLICY_ARN
access_key_suffix=${ACCESS_KEY_ID: -4}
credential_bundle=$CREDENTIAL_FILE
credential_bundle_mode=0600
RIPPLE_AWS_RAILWAY_PRINCIPAL_END
EOF
  exit 0
fi

KEY_JSON="$(aws iam create-access-key --user-name "$IAM_USER" --output json)"
ACCESS_KEY_ID="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["AccessKey"]["AccessKeyId"])' <<<"$KEY_JSON")"

rollback() {
  local status=$?
  trap - EXIT
  if [[ $status -ne 0 && -n "${ACCESS_KEY_ID:-}" ]]; then
    aws iam delete-access-key --user-name "$IAM_USER" --access-key-id "$ACCESS_KEY_ID" >/dev/null 2>&1 || true
    rm -f "$CREDENTIAL_FILE" >/dev/null 2>&1 || true
  fi
  unset KEY_JSON
  exit "$status"
}
trap rollback EXIT

umask 077
mkdir -p "$(dirname "$CREDENTIAL_FILE")"

# Pipe the one-time credential JSON to the writer: it never appears in argv,
# exported environment variables, stdout, or repository content.
printf '%s' "$KEY_JSON" | python3 -c '
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1]).expanduser()
region, table, profile_arn, log_group, log_stream = sys.argv[2:]
key = json.load(sys.stdin)["AccessKey"]
values = {
    "AWS_ACCESS_KEY_ID": key["AccessKeyId"],
    "AWS_SECRET_ACCESS_KEY": key["SecretAccessKey"],
    "AWS_REGION": region,
    "RIPPLE_STATE_BACKEND": "dynamodb",
    "RIPPLE_DYNAMODB_TABLE": table,
    "RIPPLE_CHANGE_INTERPRETER": "bedrock",
    "RIPPLE_BEDROCK_MODEL_ID": profile_arn,
    "RIPPLE_TRACE_BACKEND": "cloudwatch",
    "RIPPLE_CLOUDWATCH_LOG_GROUP": log_group,
    "RIPPLE_CLOUDWATCH_LOG_STREAM": log_stream,
    "RIPPLE_REQUIRE_AWS_RUNTIME": "true",
}
out.write_text("".join(f"{name}={value}\n" for name, value in values.items()), encoding="utf-8")
out.chmod(0o600)
' "$CREDENTIAL_FILE" "$AWS_REGION" "$TABLE" "$PROFILE_ARN" "$LOG_GROUP" "$LOG_STREAM"

KEY_SUFFIX="${ACCESS_KEY_ID: -4}"
unset KEY_JSON
trap - EXIT

cat <<EOF
RIPPLE_AWS_RAILWAY_PRINCIPAL_BEGIN
status=PASS
iam_user=$IAM_USER
runtime_policy_arn=$POLICY_ARN
access_key_suffix=$KEY_SUFFIX
credential_bundle=$CREDENTIAL_FILE
credential_bundle_mode=0600
RIPPLE_AWS_RAILWAY_PRINCIPAL_END

The credential bundle contains the only copy of the new secret access key.
Do not print, commit, email, or paste that file into ChatGPT.
Import its variables directly into the private Railway ripple-v12 environment, then delete the local bundle after the cutover is verified.
EOF
