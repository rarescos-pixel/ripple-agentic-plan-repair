# Ripple — AWS runtime credentials and identity

## Current decision

The canonical public Ripple runtime now runs on **AWS ECS Express Mode / Fargate**. It does **not** use static AWS access keys in the application container.

Runtime AWS access is provided by IAM roles:

- `RippleEcsTaskExecutionRole` — image pull, logs and SSM-backed startup secrets required by ECS;
- `RippleEcsTaskRole` — the application runtime policy for DynamoDB, Bedrock and CloudWatch;
- `RippleEcsInfrastructureRole` — ECS Express infrastructure operations.

GitHub Actions uses short-lived OIDC federation into `RippleGitHubOidcRole` for bounded deployment/proof operations. The final cutover flow temporarily extends only the minimum role-management permissions needed to register an exact-SHA task definition, then restores service-only infrastructure trust and removes the temporary bootstrap policy after a successful proof.

No AWS access key or secret access key is committed to Git, stored in the container image, printed to CI logs, or required by the canonical application runtime.

## Application secrets

The OAuth service-client secret and demo-user password are stored as AWS Systems Manager Parameter Store `SecureString` values under:

- `/ripple/canonical/service-client-secret`
- `/ripple/canonical/demo-user-password`

The task definition references those parameter ARNs; values are injected at task startup and are not embedded in repository files or the ECR image.

## Required runtime configuration

The canonical task definition sets:

- `AWS_REGION=eu-central-1`
- `RIPPLE_ENV=production`
- `RIPPLE_STATE_BACKEND=dynamodb`
- `RIPPLE_DYNAMODB_TABLE=ripple-canonical-state`
- `RIPPLE_CHANGE_INTERPRETER=bedrock`
- `RIPPLE_BEDROCK_MODEL_ID=eu.amazon.nova-2-lite-v1:0`
- `RIPPLE_TRACE_BACKEND=cloudwatch`
- `RIPPLE_CLOUDWATCH_LOG_GROUP=/ripple/canonical/runtime`
- `RIPPLE_CLOUDWATCH_LOG_STREAM=runtime`
- `RIPPLE_REQUIRE_AWS_RUNTIME=true`
- the exact release SHA exposed by `/readyz` for release verification.

Production validation fails closed if only part of the DynamoDB + Bedrock + CloudWatch structural runtime is configured.

## Exact-SHA cutover proof

A release is canonical only after all of these pass against the public AWS endpoint:

1. ECS converges to the exact registered task definition and immutable ECR digest;
2. `/readyz` repeatedly reports `runtime_mode=aws-structural`, the three required components and the exact Git SHA;
3. authenticated OAuth + MCP 2025-11-25 smoke passes;
4. Bedrock normalization is live;
5. the exact plan produces five authoritative receipts;
6. a fresh MCP session resolves the same semantic change and exact snapshot;
7. replay is `5/5 deduplicated` and the authoritative unique-write count remains unchanged (`5 -> 5`), proving **0 new provider writes**;
8. CloudWatch contains the execution trace;
9. the ECR digest is re-read and matches the deployed digest.

## Historical Railway path

An earlier design considered keeping Railway as the public MCP host and provisioning a dedicated IAM user or IAM Roles Anywhere for access to AWS backends. That path is now superseded. It is retained only in repository history as an audit trail of the credential-safety decision that led to moving the canonical runtime into AWS instead of introducing long-lived static workload credentials.

## Security invariant

The deployment path must never solve an infrastructure problem by widening permanent runtime authority. Temporary bootstrap permissions are acceptable only when bounded, auditable, removed after proof, and never inherited by the application task role.
