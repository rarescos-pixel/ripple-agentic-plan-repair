# Ripple — AWS direct live evidence

Status: **PASS for the independent direct AWS structural proof.** This report is historical evidence from the phase before the canonical public runtime moved to AWS ECS Express Mode / Fargate.

## Verified live AWS proof

GitHub Actions workflow: `AWS live evidence probe (non-blocking)`

- run: `34026664647`
- job: `101468741362`
- source SHA exercised: `fc6d38dfc4ebe57aa6fe2623ba86618b5ea85c4f`
- region: `eu-central-1`

Observed markers:

```text
AWS_OIDC=PASS
DYNAMODB_LIVE=PASS
DYNAMODB_RECEIPT_LIVE=PASS
AWS_REPLAY_DEDUP=PASS
BEDROCK_MODEL=eu.amazon.nova-2-lite-v1:0
BEDROCK_LIVE=PASS
CLOUDWATCH_LOGS_LIVE=PASS
AWS_DYNAMODB_STRUCTURAL_EVIDENCE=PASS
AWS_DYNAMODB_REPLAY_DEDUP=PASS
AWS_BEDROCK_STATUS=PASS
AWS_CLOUDWATCH_STATUS=PASS
AWS_DIRECT_LIVE_EVIDENCE=PASS
```

The CloudWatch proof was write **and readback**, not only a successful API call. The DynamoDB proof conditionally wrote one receipt, verified replay rejection and read the authoritative receipt back. Bedrock performed a real Nova 2 Lite inference with a bounded normalization request.

## Trust boundary

AWS access for this proof used GitHub OIDC to assume `RippleGitHubOidcRole`. No static AWS access key was committed to the repository or printed by the proof.

## What this report proves

- Amazon Bedrock / Nova 2 Lite was live and callable by Ripple's controlled AWS path;
- DynamoDB state/idempotency semantics were exercised live;
- CloudWatch structured trace write/readback was exercised live;
- AWS was structural project infrastructure before the public compute migration.

## Current architecture supersedes the old boundary

At the time this report was first generated, Railway was still the public MCP host and the AWS-backed public-runtime cutover was pending. That boundary is now obsolete.

The canonical public runtime now runs on **AWS ECS Express Mode / Fargate** and uses DynamoDB + Bedrock + CloudWatch in the serving process. The current stronger proof is defined in `docs/AWS_READINESS.md` and the exact-SHA canonical release workflow: immutable ECR digest → ECS convergence → repeated public exact-SHA `/readyz` → authenticated MCP/AWS smoke → fresh-session replay with authoritative write count unchanged (`5 → 5`) → CloudWatch trace readback → digest verification.

This file is intentionally retained because the earlier direct proof is independent historical evidence, not because it defines the current claim boundary.
