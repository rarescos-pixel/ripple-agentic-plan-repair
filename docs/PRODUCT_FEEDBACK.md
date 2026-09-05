# Product Feedback — Amazon Developer Hackathon

This document is written to match the required submission questions. It distinguishes **observed/runtime feedback** from **integration/setup feedback** so that Ripple does not claim an Amazon service was exercised live before evidence exists.

## Alexa+ self-hosted MCP path

### Which developer tools, APIs and SDKs did you use and for what?

Ripple uses the Alexa+ **self-hosted MCP server** path with MCP `2025-11-25` Streamable HTTP as the agent surface. We implemented the protocol, OAuth discovery/authorization, tool schemas and a Repair Card MCP App resource. We also prepared the Alexa+ add-on package/media surfaces used by the onboarding/inspection flow.

The public MCP server exposes five tools: record a changed fact, preview a repair plan, approve the exact repair, execute bounded actions and query repair status.

### What worked well?

- The self-hosted MCP path is a strong fit for agentic products that need their own deterministic policy and state rather than pushing all behavior into a prompt.
- The minimum MCP version requirement is explicit and the Streamable HTTP transport maps cleanly to a normal HTTPS service.
- MCP tool separation made Ripple's safety boundary easy to express: preview, approval and execution are distinct operations that can be tested independently.
- The MCP App resource model lets a visual Repair Card complement voice without moving execution authority into the UI.
- Once the interoperability details were pinned, the public service could be tested end to end from an independent remote container rather than only locally.

### What needs work?

- A complete Alexa+ OAuth example should include the **refresh-token exchange**, not only initial authorization. Our strict implementation initially expected the resource binding to be repeated, while the Alexa-compatible refresh path omitted `resource`. A wrong explicit resource still needs rejection. One normative transcript would remove ambiguity.
- The current Local Inspector guide documents MCP POSTs with `Accept: application/json`, while a strict Streamable HTTP implementation commonly validates the dual JSON + SSE Accept form. The sample also advertises an older client protocol version before the server negotiates its required `2025-11-25` version. That difference is easy to miss and can produce an HTTP 406 before tool discovery even when the server passes its normal MCP conformance suite. The docs should either align the example with the transport contract or explicitly say that Inspector intentionally uses JSON-only Accept and expects the server to tolerate it.
- The visual integration path spans base MCP, Alexa+ guidance and the MCP Apps extension. A single canonical sample should show tool metadata → `ui://` resource → `resources/read` → MIME profile → host lifecycle in one place.
- Add-on packaging would benefit from an official preflight validator that checks the manifest and resolves every public media/privacy/terms URL, verifies required image sizes/content types and catches missing packaged resources before onboarding.
- Access/onboarding boundaries should be stated prominently: what can every hackathon participant run locally, what requires an enabled Alexa+ partner/developer surface, and what evidence is acceptable when an official client surface is unavailable.

### How was onboarding from zero to hello world?

Getting a basic self-hosted MCP endpoint running was straightforward. The expensive part was moving from “MCP tool calls work” to an Alexa-ready product surface: OAuth refresh interoperability, Local Inspector request-shape compatibility, visual-resource binding, store/package assets, public media behavior and evidence that the deployed artifact actually contains what the manifest references.

We solved that by building independent gates for protocol behavior, the documented Inspector request shape, OAuth refresh, MCP App safety and store media rather than treating a successful deployment status as proof.

### Would you build with Alexa+ / this path again?

**Yes.** The self-hosted MCP model is especially attractive for workflows where Alexa should orchestrate but must not own the application's money, safety or idempotency policy. It lets voice be the low-friction input while deterministic application code remains authoritative.

---

## MCP App / Alexa+ visual decision surface

### Which tools did you use and for what?

Ripple uses an MCP App resource for the Repair Card. The card renders the consequence set, dollars at risk, repair cost, net value preserved and the exact approval CTA. It is intentionally display-only and cannot invoke approval/execution.

### What worked well?

- The UI resource is transportable with the MCP tool instead of requiring a separate proprietary dashboard API.
- Theme/context and resize hooks are enough for a compact decision card.
- Keeping visual output separate from the tool's authority made it possible to enforce a strong static safety gate.

### What needs work?

- The documentation should make the distinction between `structuredContent` and a renderable MCP App resource impossible to miss.
- One official Alexa-oriented reference implementation covering the full lifecycle would reduce cross-document interpretation.
- A local validator that renders the resource in the same constraints as the Alexa host would catch visual/packaging issues earlier.

### Onboarding

The conceptual model is good, but the first integration requires understanding several specifications at once. After the contract was clear, the implementation itself was small and stable.

### Would you build with it again?

**Yes.** For Ripple, the card materially improves the Alexa experience because the user can hear the recommendation and visually verify the exact money/scope before approval.

---

## AWS Builder — Bedrock, DynamoDB, CloudWatch, IAM and Budgets

### Current evidence status

The AWS integration is **implemented and AWS-ready, but not yet AWS-live verified**. The comments below therefore cover architecture/setup work that has actually been done. Runtime performance/reliability feedback will be added only after the live stack and Railway cutover are exercised. This distinction is deliberate.

### Which services are being used and for what?

- **Amazon Bedrock:** normalize a natural-language changed fact into one constrained structured change event. Bedrock is not allowed to choose repairs or execute provider actions.
- **Amazon DynamoDB:** persist approvals, idempotency records and authoritative receipts across process/session restarts.
- **Amazon CloudWatch Logs:** store bounded, redacted structured traces.
- **IAM:** least-privilege policy scoped to the Ripple table, trace stream and Bedrock inference profile.
- **AWS Budgets:** cost guardrails for the hackathon project.
- **CloudFormation:** reproducible deployment of the above resources.

### What worked well during implementation/setup?

- DynamoDB's conditional-write semantics map naturally to authoritative idempotency receipts.
- Bedrock's Converse/tool-use boundary can be constrained so the model only proposes structured normalization while deterministic code stays authoritative.
- CloudFormation makes the AWS Builder claim auditable: the intended resources, retention, PITR, budget and policy are visible in code.
- Resource-scoped IAM is a better story for an externally hosted MCP runtime than broad account credentials.

### What needs work?

- External-workload credential guidance is operationally heavy for small PaaS-hosted services. IAM Roles Anywhere is robust but introduces CA/trust-anchor/certificate lifecycle; not every PaaS exposes a workload OIDC token suitable for AWS STS.
- A concise AWS guide for **external PaaS → Bedrock + DynamoDB + CloudWatch** should compare OIDC federation, Roles Anywhere and bounded temporary fallbacks, including rotation and teardown.
- Bedrock model IDs vs geographic/application inference profiles are powerful but add conceptual overhead. A “choose a model for production invocation in region X” flow that outputs the correct profile form and explains when each ID is required would reduce setup errors.

### Onboarding

The AWS application code and IaC were straightforward to make testable. The largest design cost was the credential boundary between a Railway-hosted public service and AWS. Ripple therefore treats credential lifecycle, rollback and teardown as first-class testable artifacts rather than manual notes.

### Would you build with these AWS services again?

**Provisionally yes, pending the live gate.** The service boundaries fit the product well: Bedrock for narrow language interpretation, DynamoDB for durable idempotent state, and CloudWatch for evidence. The final answer in the Devpost submission will be based on the live deployment/run, not only the design-stage experience.

---

## Feature requests

### 1. Alexa+ self-hosted MCP interoperability validator — **Important**

A CLI/Inspector mode that validates OAuth discovery, authorization + refresh behavior, MCP protocol version, JSON/SSE Accept compatibility, tool schemas, `ui://` resources, MCP App MIME/lifecycle, and public package assets in one run.

Why it matters: a service can be healthy at the HTTP/container level while still failing a specific Alexa onboarding contract.

### 2. Official external-PaaS AWS workload identity recipes — **Important**

Reference implementations for common non-AWS runtimes showing the preferred short-lived credential path, fallback trade-offs and teardown.

Why it matters: many hackathon projects keep an existing public host but want AWS to be a structural backend without embedding long-lived broad credentials.

## Linked friction evidence

See [`FRICTION_LOG.md`](FRICTION_LOG.md) for step-by-step entries with expected vs actual behavior, severity, workaround and actionable suggestions.
