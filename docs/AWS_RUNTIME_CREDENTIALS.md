# Ripple — AWS credentials for the external Railway runtime

## Decision

Ripple keeps Railway as the public MCP host. The AWS runtime components are structural: DynamoDB stores approvals and authoritative receipts, Bedrock normalizes only the changed fact, and CloudWatch stores redacted structured traces.

The preferred AWS pattern for a workload outside AWS is temporary credentials. AWS documents IAM Roles Anywhere for non-AWS servers, containers, and applications, but that requires an X.509 certificate authority, a trust anchor, workload certificates/private keys, and the Roles Anywhere credential helper. See:

- https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios_non-aws.html
- https://docs.aws.amazon.com/rolesanywhere/latest/userguide/introduction.html

For this short-lived hackathon runtime, Railway currently provides no service workload OIDC/JWT that can be exchanged directly with AWS STS. Adding a CA/PKI solely for Ripple would add infrastructure, operating cost, certificate lifecycle, and another failure mode without improving the judged product behavior.

Therefore the temporary deployment compromise is a **dedicated IAM user with no console login and exactly one access key**, attached only to the CloudFormation-created `RuntimePolicy`. The policy itself is resource-scoped to the Ripple DynamoDB table, CloudWatch stream, and Bedrock Application Inference Profile.

This is deliberately not described as the ideal long-term AWS architecture. If Railway exposes workload identity later, or if Ripple becomes a persistent production service, migrate to short-lived federated credentials / IAM Roles Anywhere and revoke the IAM user key.

## Secret-handling invariant

`scripts/aws_railway_runtime_principal.sh` runs only after `aws_live_verify.py` succeeds. It:

1. creates/reuses `ripple-railway-runtime`;
2. attaches only the stack output `RuntimePolicyArn`;
3. refuses to create a second active key;
4. creates one access key;
5. writes the key and complete AWS runtime configuration to `~/.ripple/railway-aws.env` with mode `0600`;
6. never prints the secret key or credential bundle;
7. revokes the newly created key if bundle creation fails.

The bundle is a private transfer artifact. It must go directly from the authenticated AWS environment into Railway private variables. It must never enter Git, CI logs, screenshots, email, issue text, Devpost, or ChatGPT.

## Required private Railway variables

The bundle contains exactly the values needed by the canonical service:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `RIPPLE_STATE_BACKEND=dynamodb`
- `RIPPLE_DYNAMODB_TABLE=...`
- `RIPPLE_CHANGE_INTERPRETER=bedrock`
- `RIPPLE_BEDROCK_MODEL_ID=...`
- `RIPPLE_TRACE_BACKEND=cloudwatch`
- `RIPPLE_CLOUDWATCH_LOG_GROUP=...`
- `RIPPLE_CLOUDWATCH_LOG_STREAM=runtime`
- `RIPPLE_REQUIRE_AWS_RUNTIME=true`

No AWS credential belongs in the repository.

## Cutover proof

After those variables are applied atomically to `ripple-v12`:

1. `/readyz` must report `runtime_mode=aws-structural`, `structural_aws_runtime=true`, and the three component names without resource identifiers;
2. `scripts/aws_runtime_smoke.py` must pass against the public MCP endpoint;
3. the first session must execute five writes;
4. a fresh MCP session must resolve the same canonical change and plan snapshot but produce `5/5 deduplicated` with `0 provider writes`;
5. Bedrock trace correlation IDs must differ between invocations while the semantic change ID remains stable.

Only after those checks may the project claim a live structural AWS runtime.

## Cleanup

`scripts/aws_teardown.sh` revokes and deletes all access keys for the dedicated runtime user, detaches the Ripple runtime policy, deletes the IAM user, removes the local credential bundle, then deletes the CloudFormation stack.

Keep the principal only for the period in which the live judging endpoint needs AWS. Rotate immediately if the key is ever suspected to have been exposed.
