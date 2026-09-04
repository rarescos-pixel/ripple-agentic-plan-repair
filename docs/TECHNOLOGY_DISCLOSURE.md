# Technology Disclosure — real vs simulated

## Real, implemented and publicly exercised
- public HTTPS MCP Streamable HTTP server, protocol `2025-11-25`;
- MCP initialization/session lifecycle, tool discovery/calls and session deletion;
- OAuth protected-resource and authorization-server discovery;
- service client credentials and user authorization-code + PKCE S256 flows;
- deterministic dependency graph traversal and impact predicates;
- exact-content approval boundary;
- preflight, idempotent execution, execution receipts and replay safety;
- independent remote smoke from a separate Railway container;
- judge-facing web simulation over the same deterministic safety model;
- executable adversarial evaluation matrix.

## Real code, not yet connected to live AWS
- injectable Bedrock `Converse` interpreter boundary, tested with a fake client;
- AWS architecture/cost controls for Bedrock + Lambda + DynamoDB + CloudWatch.

## Simulated provider integrations
- CalendarTool
- RideTool
- ReservationTool
- DeliveryTool
- CareServiceTool

These adapters mutate deterministic demo state only. They do not alter real user accounts, make real bookings, notify real people or move real money.

## Demo infrastructure limitations
The bundled OAuth/token/session stores and idempotency ledger are in-memory. The Railway demo remains single-instance; process restart durability is not claimed. This is hackathon identity/runtime infrastructure, not a production identity provider.

## Not claimed yet
- actual Alexa+ production/onboarding client connection;
- live Amazon Bedrock invocation;
- Lambda/DynamoDB/CloudWatch runtime evidence;
- real airline/ride/reservation/delivery/care transactions.

## Submission integrity rule
Every final Devpost claim must be backed by source + test/runtime evidence, or explicitly labeled simulated/target architecture.
