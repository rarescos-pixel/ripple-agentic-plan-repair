# Product Feedback — Amazon Developer Hackathon

This document answers the submission feedback questions and separates observed behavior from historical integration friction.

## Alexa+ self-hosted MCP path

### Which developer tools, APIs and SDKs did you use and for what?

Ripple uses the Alexa+ **self-hosted MCP server** path with MCP `2025-11-25` Streamable HTTP. We implemented OAuth discovery/authorization, tool schemas, stateful MCP sessions, five bounded tools, and a display-only Repair Card MCP App resource. The Alexa+ add-on package points at the canonical public AWS MCP endpoint.

### What worked well?

- Self-hosted MCP is a strong fit when deterministic safety, money policy and idempotency must remain application-owned.
- Tool separation makes preview, exact approval and execution independently testable.
- The MCP App lets voice and screen share the same decision surface without giving the UI execution authority.
- Once interoperability was pinned down, the public service could be tested end to end from an independent runner rather than only locally.

### What needs work?

- A canonical Alexa+ OAuth example should include refresh-token exchange and explicitly document whether `resource` is omitted on refresh while a wrong explicit resource still fails closed.
- Local Inspector examples should align their `Accept` headers and protocol-version examples with the Streamable HTTP contract, or explicitly document intended compatibility behavior.
- One Alexa-oriented MCP App example should show tool metadata → `ui://` resource → `resources/read` → MIME profile → host lifecycle in one place.
- Add-on packaging would benefit from an official preflight validator that resolves every endpoint/media/privacy/terms URL and validates required image sizes and content types.

### How was onboarding from zero to hello world?

A basic MCP endpoint was straightforward. The expensive part was moving from “tool calls work” to a judge-ready Alexa surface: OAuth refresh interoperability, Inspector request shape, visual-resource binding, package assets, public media behavior and exact deployed-artifact evidence. Ripple addressed this with executable gates rather than treating deployment status as proof.

### Would you build with Alexa+ / this path again?

**Yes.** Voice is the low-friction input, while deterministic application code remains authoritative for money, approval and idempotency.

---

## MCP App / visual decision surface

### Which tools did you use and for what?

Ripple uses a display-only MCP App Repair Card to show the consequence set, dollars at risk, repair cost, net value preserved, “Why this plan?” evidence and execution receipts.

### What worked well?

- The resource travels with MCP rather than requiring a separate dashboard API.
- Preview and execution can bind to the same visual surface.
- Static safety gates can prove the UI cannot approve or execute actions.

### What needs work?

- The distinction between `structuredContent` and a renderable MCP App resource should be more prominent.
- An official Alexa-oriented reference implementation and local renderer/validator would reduce integration ambiguity.

### Would you build with it again?

**Yes.** For Ripple, the card materially improves the voice experience because the user can verify exact money/scope before approval and inspect authoritative receipts afterward.

---

## AWS Builder — ECS Express Mode/Fargate, Bedrock, DynamoDB, CloudWatch, IAM and Budgets

### Current evidence status

**AWS services are live and structurally verified, and the canonical public runtime now runs on AWS ECS Express Mode / Fargate.** Earlier direct evidence separately proved real Nova 2 Lite inference, DynamoDB conditional receipt semantics and CloudWatch write/readback. The canonical release path now goes further: it deploys one exact Git SHA as an immutable ECR image, requires ECS control-plane convergence and repeated public exact-SHA readiness, then runs authenticated AWS/MCP replay proof against that public endpoint.

### Which services are being used and for what?

- **Amazon ECS Express Mode / Fargate:** canonical public HTTPS MCP runtime.
- **Amazon Bedrock / Nova 2 Lite:** normalize one natural-language changed fact into a constrained structured ChangeEvent; it never chooses the money-spending repair.
- **Amazon DynamoDB:** durable exact proposal/approval state, idempotency records and authoritative receipts.
- **Amazon CloudWatch Logs:** bounded redacted traces used for execution/recovery evidence.
- **IAM task roles + GitHub OIDC:** runtime and deployment identity without static AWS credentials in Git or the container image.
- **AWS Budgets / anomaly controls:** cost guardrails.

### What worked well during implementation and live verification?

- DynamoDB conditional-write semantics map naturally to authoritative idempotency receipts.
- Bedrock works well as a narrow language-normalization boundary while deterministic code owns old state, economic choice, approval and execution.
- CloudWatch provides independently inspectable execution traces without raw-secret logging.
- ECS task roles remove the static-credential problem that existed when the service was hosted outside AWS.
- GitHub OIDC supports temporary deployment authority; the cutover workflow restores service-only infrastructure trust after task-definition registration.
- ECS canary deployment and rollback behavior provided a useful fail-safe while we diagnosed an infrastructure-role identity issue.

### What needs work?

- ECS Express Mode documentation should make the lifecycle of its infrastructure role and any service-side credential binding more explicit. Recreating an apparently equivalent infrastructure role can behave differently from updating its trust policy in place because identity continuity matters.
- A first-party “exact source revision → immutable ECR digest → ECS deployment → public endpoint” evidence recipe would help hackathon teams prove what is actually serving.
- Bedrock model IDs versus geographic/application inference profiles remain conceptually expensive for first-time users.
- Alexa+ + AWS examples would benefit from one end-to-end reference architecture for a self-hosted MCP service running directly on ECS/Fargate with OAuth and task roles.

### How was onboarding?

The application-side AWS calls were straightforward once identity was correct. The hardest part was deployment identity and proving that the exact source revision seen by judges was the one running publicly. Ripple therefore treats role identity, exact-SHA deployment, public readiness, replay semantics and cleanup as executable release checks.

### Would you build with these AWS services again?

**Yes.** ECS/Fargate plus task roles is a cleaner canonical runtime for this project than an external host with long-lived AWS credentials; Bedrock, DynamoDB and CloudWatch also fit Ripple's narrow interpretation, durable idempotency and evidence needs.

---

## Feature requests

### 1. Alexa+ self-hosted MCP interoperability validator — Important

A CLI/Inspector mode that validates OAuth discovery + refresh, MCP protocol version, JSON/SSE Accept compatibility, tool schemas, `ui://` resources, MCP App MIME/lifecycle and public package assets in one run.

### 2. Exact-deployment evidence recipe for ECS — Important

A documented pattern that binds a Git source revision to an immutable ECR digest, task definition, ECS service revision and public readiness endpoint, including safe rollback and task-role verification.

### 3. ECS Express infrastructure-role identity guidance — Important

Document when role identity continuity matters and recommend in-place trust/policy changes over delete/recreate when the service may retain identity-bound infrastructure state.

## Linked friction evidence

See [`FRICTION_LOG.md`](FRICTION_LOG.md) for step-by-step expected-vs-actual entries and [`AWS_DIRECT_LIVE_EVIDENCE.md`](AWS_DIRECT_LIVE_EVIDENCE.md) for the earlier independent direct AWS proof that preceded the canonical ECS runtime cutover.
