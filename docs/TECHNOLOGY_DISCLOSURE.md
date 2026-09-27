# Technology Disclosure — real vs simulated

## Real, implemented and publicly exercised
- canonical public HTTPS MCP Streamable HTTP server on Amazon ECS Express Mode / Fargate, protocol `2025-11-25`;
- MCP initialization/session lifecycle, tool discovery/calls and session deletion;
- OAuth protected-resource and authorization-server discovery;
- service client credentials and user authorization-code + PKCE S256 flows;
- deterministic dependency graph traversal and impact predicates;
- exact-content approval boundary;
- preflight, idempotent execution, execution receipts and replay safety;
- durable exact proposal/approval/idempotency/receipt state in DynamoDB;
- real Amazon Bedrock / Nova 2 Lite changed-fact normalization;
- redacted structured runtime tracing in CloudWatch Logs;
- ECS task-role runtime identity with no static AWS application credentials;
- GitHub OIDC for bounded deployment/proof authority;
- one bounded real external provider path through GitHub Issues with write/readback/replay-dedup/restore proof;
- judge-facing web simulation over the same deterministic safety model;
- executable adversarial evaluation matrix.

Canonical public MCP endpoint:

`https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws/mcp`

A frozen release is considered canonical only after exact-SHA readiness, authenticated MCP/OAuth smoke, Bedrock live normalization, DynamoDB fresh-session replay with zero duplicate writes, CloudWatch execution evidence and ECR digest readback all pass for the same release.

## Historical Railway evidence

An earlier hosting phase used Railway for the public MCP process and independent smoke runners. Those reports remain in the repository as historical audit evidence because they document real interoperability defects and remote execution behavior discovered during development.

Railway is **not** the current public runtime, is **not** required for judging, and is **not** part of the current release freeze sequence.

## Simulated provider integrations
- CalendarTool
- RideTool
- ReservationTool
- DeliveryTool
- CareServiceTool

These adapters mutate deterministic demo state only. They do not alter real user accounts, make real bookings, notify real people or move real money.

The GitHub Issues provider is the deliberately narrow real external-provider exception and is separately allowlisted, reversible and evidence-bounded.

## Current demo/runtime limitations

- the embedded OAuth identity surface is hackathon/demo infrastructure, not a production identity provider;
- airline/ride/reservation/delivery/pet-care/calendar production integrations are not claimed;
- fixture dollar amounts are deterministic scenario values, not market prices or market-size estimates;
- no actual Alexa+ production-client session is claimed unless separately exercised and evidenced.

## AWS runtime boundary

The canonical application runtime uses:

- **Amazon ECS Express Mode / Fargate** — public MCP compute and HTTPS ingress;
- **Amazon Bedrock / Nova 2 Lite** — constrained changed-fact normalization;
- **Amazon DynamoDB** — durable proposal/approval/idempotency/receipt state;
- **Amazon CloudWatch Logs** — redacted structured traces;
- **IAM task roles** — runtime authority;
- **GitHub OIDC** — short-lived deployment/proof authority;
- **AWS Budgets / anomaly controls** — spend guardrails.

No AWS access key or secret access key is committed to the repository or required by the canonical application container.

## Submission integrity rule

Every final Devpost claim must be backed by source + test/runtime evidence, or explicitly labeled simulated/target architecture. Historical Railway evidence must never be presented as the current public runtime.
