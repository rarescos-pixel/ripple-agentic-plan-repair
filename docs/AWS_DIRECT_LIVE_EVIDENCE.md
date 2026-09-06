# Ripple — AWS direct live evidence

Status: **PASS for direct AWS structural evidence; public Railway AWS-runtime cutover remains pending.**

This document records what has actually been exercised against AWS and keeps that claim separate from the stronger claim that the canonical public Railway MCP process is already using AWS for every request.

## Verified live AWS proof

GitHub Actions workflow: `AWS live evidence probe (non-blocking)`

- run: `34026664647`
- job: `101468741362`
- source SHA exercised: `fc6d38dfc4ebe57aa6fe2623ba86618b5ea85c4f`
- region: `eu-central-1`

Observed markers from the completed job:

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

The CloudWatch proof is write **and readback**, not only a successful API call. The DynamoDB proof writes one receipt conditionally, verifies the replay is rejected by the conditional write, and reads the authoritative receipt back consistently. Bedrock performs a real Nova 2 Lite inference with a bounded normalization request.

## Trust boundary

AWS access for these proof runs uses GitHub OIDC to assume the dedicated `RippleGitHubOidcRole`. No static AWS access key is committed to the repository or printed by the proof.

## Claim boundary

What this evidence supports:

- Amazon Bedrock / Nova 2 Lite is live and callable by Ripple's controlled AWS path;
- DynamoDB live state/idempotency semantics are exercised;
- CloudWatch Logs live trace write/readback is exercised;
- AWS is structural project infrastructure rather than a diagram-only claim.

What this evidence does **not** yet support:

- that the canonical `ripple-v12` Railway process is currently configured with `RIPPLE_STATE_BACKEND=dynamodb`, `RIPPLE_CHANGE_INTERPRETER=bedrock`, and `RIPPLE_TRACE_BACKEND=cloudwatch` for every public request;
- that the latest final submission SHA has already been deployed to Railway and passed a post-cutover AWS-backed public smoke.

Those stronger claims remain gated by the credential-safe Railway cutover and exact-revision public smoke. This separation is deliberate: evidence must remain stronger than marketing copy.
