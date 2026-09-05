#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-eu-central-1}"
STACK_NAME="${RIPPLE_AWS_STACK_NAME:-ripple-demo}"
IAM_USER="${RIPPLE_RUNTIME_IAM_USER:-ripple-railway-runtime}"
CREDENTIAL_FILE="${RIPPLE_RUNTIME_CREDENTIAL_FILE:-$HOME/.ripple/railway-aws.env}"

POLICY_ARN="$(aws cloudformation describe-stacks \
  --region "$AWS_REGION" \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`RuntimePolicyArn`].OutputValue | [0]' \
  --output text)"

if aws iam get-user --user-name "$IAM_USER" >/dev/null 2>&1; then
  while read -r key_id; do
    [[ -z "$key_id" ]] && continue
    aws iam update-access-key --user-name "$IAM_USER" --access-key-id "$key_id" --status Inactive >/dev/null
    aws iam delete-access-key --user-name "$IAM_USER" --access-key-id "$key_id" >/dev/null
  done < <(aws iam list-access-keys --user-name "$IAM_USER" --query 'AccessKeyMetadata[].AccessKeyId' --output text | tr '\t' '\n')

  if [[ -n "$POLICY_ARN" && "$POLICY_ARN" != "None" ]]; then
    aws iam detach-user-policy --user-name "$IAM_USER" --policy-arn "$POLICY_ARN" >/dev/null 2>&1 || true
  fi
  aws iam delete-user --user-name "$IAM_USER"
  echo "Revoked and deleted IAM runtime principal $IAM_USER"
fi

rm -f "$CREDENTIAL_FILE"

aws cloudformation delete-stack --region "$AWS_REGION" --stack-name "$STACK_NAME"
aws cloudformation wait stack-delete-complete --region "$AWS_REGION" --stack-name "$STACK_NAME"
echo "Deleted $STACK_NAME in $AWS_REGION"
