# Product Feedback — Amazon Developer Hackathon

This document is written to match the required submission questions. It distinguishes **observed/runtime feedback** from **integration/setup feedback** and keeps direct live AWS evidence separate from the stronger claim that the canonical public Railway process has completed its AWS-backed cutover.

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

Ripple uses an MCP App resource for the Repair Card. The card renders the consequence set, dollars at risk, repair cost, net value preserved, deterministic “Why this plan?” evidence and the execution receipt timeline. It is intentionally display-only and cannot invoke approval/execution.

### What worked well?

- The UI resource is transportable with the MCP tool instead of requiring a separate proprietary dashboard API.
- Theme/context and resize hooks are enough for a compact decision card.
- Keeping visual output separate from the tool's authority made it possible to enforce a strong static safety gate.
- Binding both preview and execution results to the same display-only resource makes the approval boundary and post-execution receipts visually continuous without giving the UI tool authority.

### What needs work?

- The documentation should make the distinction between `structuredContent` and a renderable MCP App resource impossible to miss.
- One official Alexa-oriented reference implementation covering the full lifecycle would reduce cross-document interpretation.
- A local validator that renders the resource in the same constraints as the Alexa host would catch visual/packaging issues earlier.

### Onboarding

The conceptual model is good, but the first integration requires understanding several specifications at once. After the contract was clear, the implementation itself was small and stable.

### Would you build with it again?

**Yes.** For Ripple, the card materially improves the Alexa experience because the user can hear the recommendation, visually verify the exact money/scope before approval, then see authoritative receipts and replay safety after execution.

---

## AWS Builder — Bedrock, DynamoDB, CloudWatch, IAM and Budgets

### Current evidence status

**Direct AWS structural evidence is live verified.** A completed GitHub OIDC evidence run exercised real Amazon Nova 2 Lite inference, DynamoDB receipt write/readback plus replay rejection, and CloudWatch Logs structured-event write plus readback. The aggregate marker is `AWS_DIRECT_LIVE_EVIDENCE=PASS`.

The stronger claim that the canonical public Railway MCP process is already using those AWS backends for every request remains pending until the credential-safe Railway cutover and post-cutover exact-revision smoke pass. This distinction is deliberate.

### Which services are being used and for what?

- **Amazon Bedrock / Nova 2 Lite:** normalize a natural-language changed fact into one constrained structured change event. Bedrock is not allowed to choose repairs or execute provider actions.
- **Amazon DynamoDB:** durable proposal/approval state, idempotency records and authoritative receipts across process/session restarts.
- **Amazon CloudWatch Logs:** bounded, redacted structured traces.
- **IAM + GitHub OIDC:** least-privilege proof-run authority without committed static AWS credentials.
- **AWS Budgets / anomaly controls:** cost guardrails for the hackathon project.

### What worked well during implementation and live verification?

- DynamoDB's conditional-write semantics map naturally to authoritative idempotency receipts. The live proof confirmed that the first receipt wins, an exact replay is rejected by the conditional write, and the original authoritative receipt can be read back consistently.
- Bedrock's constrained normalization boundary works well for Ripple's safety model: Nova 2 Lite handles language interpretation while deterministic code owns old state, money arithmetic, repair policy, approval and execution.
- CloudWatch Logs can carry a small structured/redacted evidence event and provide an independent readback proof without logging the raw user utterance or credentials.
- GitHub OIDC provides a clean temporary-credential path for CI evidence and avoids static AWS keys in the repository.
- Keeping the AWS surface serverless/pay-per-use avoids adding Lambda/ECS/Fargate only for architecture-logo value.

### What needs work?

- External-workload credential guidance is operationally heavy for small PaaS-hosted services. IAM Roles Anywhere is robust but introduces CA/trust-anchor/certificate lifecycle; not every PaaS exposes a workload OIDC token suitable for AWS STS.
- A concise AWS guide for **external PaaS → Bedrock + DynamoDB + CloudWatch** should compare OIDC federation, Roles Anywhere and bounded temporary fallbacks, including rotation and teardown.
- Bedrock model IDs vs geographic/application inference profiles are powerful but add conceptual overhead. A “choose a model for production invocation in region X” flow that outputs the correct profile form and explains when each ID is required would reduce setup errors.

### Onboarding

The AWS application code and live service calls were straightforward once identity was available. The largest design cost remains the credential boundary between a Railway-hosted public service and AWS. Ripple therefore treats credential lifecycle, rollback and teardown as first-class testable artifacts rather than manual notes.

### Would you build with these AWS services again?

**Yes.** The live evidence supports the architectural fit: Bedrock for narrow language interpretation, DynamoDB for durable idempotent state, and CloudWatch for independently inspectable traces. For an external PaaS production runtime, I would still prefer short-lived workload federation over a long-lived access key whenever the host exposes a suitable identity primitive.

---

## Feature requests

### 1. Alexa+ self-hosted MCP interoperability validator — **Important**

A CLI/Inspector mode that validates OAuth discovery, authorization + refresh behavior, MCP protocol version, JSON/SSE Accept compatibility, tool schemas, `ui://` resources, MCP App MIME/lifecycle, and public package assets in one run.

Why it matters: a service can be healthy at the HTTP/container level while still failing a specific Alexa onboarding contract.

### 2. Official external-PaaS AWS workload identity recipes — **Important**

Reference implementations for common non-AWS runtimes showing the preferred short-lived credential path, fallback trade-offs and teardown.

Why it matters: many hackathon projects keep an existing public host but want AWS to be a structural backend without embedding long-lived broad credentials.

## Linked friction evidence

See [`FRICTION_LOG.md`](FRICTION_LOG.md) for step-by-step entries with expected vs actual behavior, severity, workaround and actionable suggestions. See [`AWS_DIRECT_LIVE_EVIDENCE.md`](AWS_DIRECT_LIVE_EVIDENCE.md) for the exact direct-live AWS proof and claim boundary.
