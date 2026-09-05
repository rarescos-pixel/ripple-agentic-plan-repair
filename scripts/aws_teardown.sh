#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-eu-central-1}"
STACK_NAME="${RIPPLE_AWS_STACK_NAME:-ripple-demo}"
IAM_USER="${RIPPLE_RUNTIME_IAM_USER:-ripple-railway-runtime}"
CREDENTIAL_FILE="${RIPPLE_RUNTIME_CREDENTIAL_FILE:-$HOME/.ripple/railway-aws.env}"

# Revoke the external runtime principal first and independently of stack state.
# This still works after a failed/partial stack operation, when describe-stacks
# may no longer return outputs.
if aws iam get-user --user-name "$IAM_USER" >/dev/null 2>&1; then
  while read -r key_id; do
    [[ -z "$key_id" ]] && continue
    aws iam update-access-key --user-name "$IAM_USER" --access-key-id "$key_id" --status Inactive >/dev/null
    aws iam delete-access-key --user-name "$IAM_USER" --access-key-id "$key_id" >/dev/null
  done < <(aws iam list-access-keys --user-name "$IAM_USER" --query 'AccessKeyMetadata[].AccessKeyId' --output text | tr '\t' '\n')

  while read -r policy_arn; do
    [[ -z "$policy_arn" ]] && continue
    aws iam detach-user-policy --user-name "$IAM_USER" --policy-arn "$policy_arn" >/dev/null
  done < <(aws iam list-attached-user-policies --user-name "$IAM_USER" --query 'AttachedPolicies[].PolicyArn' --output text | tr '\t' '\n')

  aws iam delete-user --user-name "$IAM_USER"
  echo "Revoked and deleted IAM runtime principal $IAM_USER"
fi

rm -f "$CREDENTIAL_FILE"

if aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$STACK_NAME" >/dev/null 2>&1; then
  aws cloudformation delete-stack --region "$AWS_REGION" --stack-name "$STACK_NAME"
  aws cloudformation wait stack-delete-complete --region "$AWS_REGION" --stack-name "$STACK_NAME"
  echo "Deleted $STACK_NAME in $AWS_REGION"
else
  echo "AWS stack $STACK_NAME is already absent; runtime credential cleanup is complete."
fi
