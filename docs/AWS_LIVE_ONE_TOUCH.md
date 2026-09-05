# Ripple — AWS live one-touch gate

This gate crosses Ripple from **AWS-ready verified** to **AWS-live resource verified** without sharing AWS credentials with ChatGPT. It also prepares the tightly-scoped private credential bundle required by the external Railway runtime.

## What it does

The bootstrap runs inside AWS CloudShell, using the AWS session already authenticated by the user. It:

1. verifies `sts:GetCallerIdentity`;
2. clones the public Ripple repository;
3. installs the AWS runtime dependency locally in CloudShell;
4. invokes **Nova Lite** and **Nova 2 Lite** against the normalization fixtures;
5. refuses to continue unless the benchmark winner is perfect on the fixture set;
6. deploys `infra/ripple-aws.json` with the winning model as the source of a tagged Bedrock Application Inference Profile;
7. provisions DynamoDB on-demand + PITR, CloudWatch Logs, the constrained runtime policy, and a monthly project budget;
8. exercises Ripple's real `DynamoDbStateStore` against the live table;
9. verifies an authoritative `executed` receipt cannot be overwritten by a later conflicting receipt;
10. emits a real CloudWatch trace and reads it back to prove secret redaction;
11. invokes the real Bedrock Application Inference Profile through Ripple's `BedrockChangeInterpreter` / Converse tool-use path;
12. verifies the AWS Budget exists;
13. only after those live checks pass, creates/reuses the no-console `ripple-railway-runtime` IAM user and attaches only the generated runtime policy;
14. refuses a second active access key, then writes the single new key plus structural runtime variables to `~/.ripple/railway-aws.env` with mode `0600`;
15. prints only non-secret evidence markers. The credential bundle itself is never printed.

## CloudShell command

Run:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/rarescos-pixel/ripple-agentic-plan-repair/main/scripts/aws_live_bootstrap.sh)
```

The script asks once for the email address that should receive AWS Budget notifications. Default region is `eu-central-1` and the default project budget is **$10/month**. Override before running only if needed:

```bash
export AWS_REGION=eu-central-1
export RIPPLE_MONTHLY_BUDGET_USD=10
```

## Safe output vs private output

Safe to retain/share as evidence:

- `RIPPLE_AWS_LIVE_VERIFY_BEGIN` / `RIPPLE_AWS_LIVE_VERIFY_END`
- `RIPPLE_AWS_RAILWAY_PRINCIPAL_BEGIN` / `RIPPLE_AWS_RAILWAY_PRINCIPAL_END`
- `RIPPLE_AWS_LIVE_HANDOFF_BEGIN` / `RIPPLE_AWS_LIVE_HANDOFF_END`

Private and never to be pasted into chat, Git, CI, email, screenshots, or submission material:

- `~/.ripple/railway-aws.env`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- any session or console credential.

## Runtime bridge

Railway currently provides no deployed-service workload OIDC/JWT that Ripple can exchange directly with AWS STS. AWS's preferred non-AWS temporary-credential mechanism, IAM Roles Anywhere, requires a CA/PKI and X.509 workload certificates. For this short-lived hackathon endpoint, Ripple therefore uses a dedicated no-console IAM user with one key and the exact resource-scoped `RuntimePolicy`; see `docs/AWS_RUNTIME_CREDENTIALS.md` for the bounded decision and cleanup contract.

The private bundle must be imported directly into the canonical `ripple-v12` Railway environment. After that cutover, the public `/readyz` endpoint must say the runtime is structurally backed by DynamoDB + Bedrock + CloudWatch, and `scripts/aws_runtime_smoke.py` must prove fresh-session durable replay with zero duplicate provider writes.

AWS-live resource verification alone is not enough to claim the Railway→AWS bridge is complete. The claim becomes complete only after the post-cutover public runtime smoke passes.
