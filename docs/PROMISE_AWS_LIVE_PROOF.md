# AWS access and service I/O: LIVE PASS at the pinned implementation SHA

**AWS OIDC + Bedrock + DynamoDB + CloudWatch: LIVE PASS.**
**CPP natural-language Intent Contract normalization: FAIL; product readiness remains blocked.**

These are separate results. A successful AWS invocation is not evidence that a
model returned a valid contract, and the invalid output was never activated.

- Implementation: `8b939542d5055f5c6c308cacdcd66667d71a0b68`, checked out explicitly and unmodified.
- Proof workflow: `.github/workflows/aws-cpp-live-proof.yml` at `15ce147c7b197b63cf99ced285af5b9521ef9a83`.
- Successful live run: [36407918402, attempt 1](https://github.com/rarescos-pixel/ripple-agentic-plan-repair/actions/runs/36407918402).
- Job: `108880966250`; region: `eu-central-1`.
- Full artifact: [10963135896](https://github.com/rarescos-pixel/ripple-agentic-plan-repair/actions/runs/36407918402/artifacts/10963135896).
- ZIP SHA-256: `9b106d9c4eecfa90128dc4fa065ae1e56d4023ec8fdb244a142c68356595210b`.
- Durable repository read-back: [PROMISE_AWS_LIVE_EVIDENCE.json](PROMISE_AWS_LIVE_EVIDENCE.json).

## What passed

| Gate | Actual observed evidence |
| --- | --- |
| OIDC / STS | Temporary federation into `RippleGitHubOidcRole`; `GetCallerIdentity` verified the expected account and role |
| Bedrock | Real Nova 2 Lite Converse/tool-use response, HTTP 200, 1,455 input and 308 output tokens, AWS request ID recorded |
| DynamoDB | The actual `DynamoPromiseStore` persisted the canonical hero; stale CAS rejected; independent consistent read matched final revision 28 |
| Durable execution | Two verified receipts; five executions after reconstructing the engine added zero provider writes |
| CloudWatch | The actual engine emitted `promise.state`; independent `GetLogEvents` returned SATISFIED and the same final ledger hash as DynamoDB |

The verified final ledger hash is
`c458305cccb086ab797bc6474f5a906b98844bac4ee22e06c5bdf0004431d5f1`.

The household contract, clock, occupancy events, provider and human approvals are
test fixtures. AWS state and traces are live. This proof does not claim physical
home actions, live Alexa interaction, or a Bedrock-generated hero contract.

## OIDC diagnosis and minimal remediation

The original PR run [36383224150](https://github.com/rarescos-pixel/ripple-agentic-plan-repair/actions/runs/36383224150)
failed at `AssumeRoleWithWebIdentity`. A direct feature-branch push
[36406741749](https://github.com/rarescos-pixel/ripple-agentic-plan-repair/actions/runs/36406741749)
also failed and recorded these non-secret claims:

```text
iss = https://token.actions.githubusercontent.com
aud = sts.amazonaws.com
sub = repo:rarescos-pixel@321760901/ripple-agentic-plan-repair@1356792571:ref:refs/heads/codex/continuous-promise-preservation
```

The same role accepted the main-branch identity:

```text
sub = repo:rarescos-pixel@321760901/ripple-agentic-plan-repair@1356792571:ref:refs/heads/main
```

This establishes the rejected and accepted branch subjects, including the
immutable GitHub owner/repository IDs. Direct `iam:GetRole` on
`RippleGitHubOidcRole` was denied in run `36406902076`; the literal trust-policy
JSON/comparison operator was therefore not readable and is not claimed here.

Only this proof workflow was added/updated on `main`. Its application checkout
remains pinned to the requested implementation SHA. The proof does not run from
pull requests or untrusted branch contexts. No IAM policy or trust relationship
was changed; no long-lived AWS key was created or exported. The session policy
further restricts access to the existing evidence table/log stream, Nova 2 Lite
inference and identity/read operations. No ECS, ECR, SSM, CloudFormation or IAM
mutation permission is included in that session policy.

The only AWS writes are evidence records in `ripple-live-evidence-state` and
events in `/ripple/live-evidence` / `github-actions`, plus bounded inference.
The public production `/readyz` remained ready at source
`c6766c5919ea903530a8da2d526d64a49b7f0578`. The new promise application was not deployed.

## Real defect found by the live test

Both Nova 2 Lite (run `36407448233`) and Nova Lite (run `36407676935`) returned
contract expressions with the unsupported literal key `operator`. Nova 2 Lite
also returned a malformed authority mapping. The implementation's strict
validator rejected the result with:

```text
ValueError: Unsupported deterministic operator: operator
```

The full response and the failure are preserved, including in the successful
AWS-access run. Its log explicitly contains `CPP_INTENT_VALIDATION=FAIL` and its
JSON records `blocks_product_readiness: true`. The workflow reports AWS access
and actual service I/O only; a green run does not waive the application failure.

The next P0 application change is an explicit, supported Intent Contract tool
schema and unambiguous expression/authority examples, followed by independent
semantic acceptance and real Bedrock validation. Such a change necessarily has a
new implementation SHA; it must not be described as fixing immutable `8b93954`.

## Reproduction

Run `AWS CPP isolated live proof` from the trusted `main` context. It checks out
the fixed implementation, performs bounded live calls, validates independent
read-backs, and uploads complete or partial evidence. Do not move the trigger to
a pull request or weaken IAM trust to make a branch token acceptable.

The evidence schema deliberately distinguishes `bedrock.status` (AWS invocation)
from `cpp_intent_validation.status` (application semantics). Both must pass before
claiming natural-language CPP readiness.
