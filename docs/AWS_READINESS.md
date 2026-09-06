# AWS readiness — canonical structural runtime

## Decision
Ripple now runs its canonical public MCP service on AWS ECS Express Mode / Fargate. AWS is no longer only a sidecar evidence layer: the public runtime itself uses the structural AWS backends that matter for correctness and proof.

## Locked structural stack
1. **Amazon ECS Express Mode / Fargate** — canonical public HTTPS MCP runtime.
2. **Amazon Bedrock / Nova 2 Lite** — one constrained changed-fact normalization per reported change; normalization only, never repair ranking or execution.
3. **DynamoDB** — durable proposal/approval state, idempotency ledger and authoritative receipts.
4. **CloudWatch Logs** — redacted structured traces for execution and recovery evidence.
5. **IAM / GitHub OIDC** — short-lived deployment authority; the runtime itself uses task roles, not static access keys.
6. **AWS Budgets / cost anomaly controls** — bounded-spend guardrails.

The deterministic Ripple engine remains the authority for dependency analysis, economic optimization, approval validation and bounded execution. The LLM has no write authority.

## Canonical public runtime

- HTTPS base: `https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws`
- MCP: `https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws/mcp`
- readiness: `/readyz`
- runtime mode: `aws-structural`
- required components: `dynamodb`, `bedrock`, `cloudwatch`

The release workflow requires the public `/readyz` response to report the exact Git source SHA before the release can be considered canonical.

## Runtime proof boundary
A valid canonical proof requires all of the following in one exact-SHA release:

- ECS control plane converges to the exact immutable ECR image digest;
- public `/readyz` repeatedly reports the exact source SHA and `aws-structural` composition;
- OAuth and MCP 2025-11-25 authenticated flows pass;
- Bedrock produces the normalized ChangeEvent;
- the five-impact plan preserves the deterministic golden economics;
- fresh-session replay returns `5/5 deduplicated`;
- the authoritative write count remains unchanged across that replay (`5 -> 5`), proving **0 new provider writes**;
- CloudWatch contains the execution trace;
- the ECR digest is re-read and matches the deployed digest.

The authoritative automation for this boundary is the final AWS canonical proof workflow in `.github/workflows/` together with `scripts/aws_runtime_smoke.py`.

## Cost controls
- one canonical Fargate task;
- one bounded Bedrock call per reported change;
- tightly bounded model output;
- DynamoDB on-demand;
- short/redacted CloudWatch evidence logging;
- no duplicate application compute tier;
- account-level budget/anomaly guardrails.

## Historical note
Earlier evidence used Railway as the public MCP host while Bedrock, DynamoDB and CloudWatch were proven separately. Those reports remain useful historical evidence, but they no longer define the canonical runtime architecture. The current canonical public service is AWS ECS Express Mode / Fargate.
