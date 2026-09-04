# Ripple — AWS live one-touch gate

This is the only user-operated step required to cross from **AWS-ready verified** to **AWS-live verified** without sharing AWS credentials with ChatGPT.

## What it does

The bootstrap runs inside AWS CloudShell, using the AWS session already authenticated by the user. It:

1. verifies `sts:GetCallerIdentity`;
2. clones the public Ripple repository;
3. installs the AWS runtime dependency locally in CloudShell;
4. invokes **Nova Lite** and **Nova 2 Lite** against the five normalization fixtures;
5. refuses to continue unless the benchmark winner is perfect on the fixture set;
6. deploys `infra/ripple-aws.json` with the winning model as the source of a tagged Bedrock Application Inference Profile;
7. provisions DynamoDB on-demand + PITR, CloudWatch Logs, the constrained runtime policy, and a monthly project budget;
8. exercises Ripple's real `DynamoDbStateStore` against the live table;
9. verifies an authoritative `executed` receipt cannot be overwritten by a later conflicting receipt;
10. emits a real CloudWatch trace and reads it back to prove secret redaction;
11. invokes the real Bedrock Application Inference Profile through Ripple's `BedrockChangeInterpreter` / Converse tool-use path;
12. verifies the AWS Budget exists;
13. prints only non-secret evidence between `RIPPLE_AWS_LIVE_VERIFY_*` and `RIPPLE_AWS_LIVE_HANDOFF_*` markers.

## CloudShell command

After this file is merged to `main`, open AWS CloudShell and run:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/rarescos-pixel/ripple-agentic-plan-repair/main/scripts/aws_live_bootstrap.sh)
```

The script asks once for the email address that should receive AWS Budget notifications. Default region is `eu-central-1` and the default project budget is **$10/month**. Override before running only if needed:

```bash
export AWS_REGION=eu-central-1
export RIPPLE_MONTHLY_BUDGET_USD=10
```

## What to return to ChatGPT

Paste only the blocks delimited by:

- `RIPPLE_AWS_LIVE_VERIFY_BEGIN` / `RIPPLE_AWS_LIVE_VERIFY_END`
- `RIPPLE_AWS_LIVE_HANDOFF_BEGIN` / `RIPPLE_AWS_LIVE_HANDOFF_END`

Do **not** paste `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, session tokens, console credentials, or any other AWS secret.

## Security boundary after this gate

Railway does not currently expose workload OIDC tokens to deployed services. Therefore the public Railway runtime cannot use an AWS IAM role through `AssumeRoleWithWebIdentity` directly. After AWS-live verification, the remaining runtime bridge must use a tightly scoped credential mechanism (or a future Railway workload-identity feature), and those credential values must be stored directly in Railway secrets—not in GitHub or ChatGPT.
