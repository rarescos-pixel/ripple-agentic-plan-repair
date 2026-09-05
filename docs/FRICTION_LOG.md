# Friction Log

Only real development friction is recorded here. Each entry follows the hackathon fields: task attempted, steps taken, expected result, actual result, severity, workaround and actionable suggestion.

Severity scale: **Critical** blocks the project; **High** blocks a major judged capability; **Medium** causes substantial rework or interoperability risk; **Low** is recoverable inconvenience.

## F1 — Alexa-compatible OAuth refresh omitted `resource`

**Date:** 2026-09-04  
**Task attempted:** Make Ripple's OAuth flow interoperable with the Alexa+ self-hosted MCP path while preserving RFC 8707-style resource binding.  
**Steps taken:** Implemented protected-resource metadata, authorization-server metadata, authorization-code + PKCE S256, refresh tokens and strict resource validation; then exercised the deployed HTTPS flow from a separate remote smoke runner.  
**Expected:** The refresh-token exchange would carry the same `resource` parameter used to bind the original user authorization.  
**Actual:** The Alexa-compatible refresh path omitted `resource`. A server that required it on refresh rejected an otherwise valid token refresh. An explicitly wrong `resource` still needed to be rejected.  
**Severity:** **High** — authentication worked initially but a valid Alexa-style refresh could fail later.  
**Workaround:** Ripple now accepts an omitted `resource` only for refresh-token exchange while continuing to reject an explicitly incorrect resource. The remote smoke test verifies both behaviors before running the full MCP repair flow.  
**Actionable suggestion:** Publish one complete Alexa+ self-hosted MCP OAuth transcript covering authorization, code exchange and **refresh**, including which RFC 8707 fields Alexa sends or omits and the expected server-side validation behavior.

**Evidence:** `docs/ALEXA_REMOTE_EVIDENCE.md`, `scripts/mcp_smoke.py`.

## F2 — Alexa visual tool results require a separate MCP App resource contract

**Date:** 2026-09-04  
**Task attempted:** Make the money-first Repair Card inspectable/renderable as an Alexa+ visual surface rather than returning only structured JSON.  
**Steps taken:** Started from the existing `preview_repair_plan` structured result, reviewed the Alexa+ Local Inspector requirements and the MCP Apps extension, then added `ui://` resource binding, `resources/list`, `resources/read`, the MCP App MIME profile, host initialization and tool-result notification handling.  
**Expected:** A well-structured MCP tool result would be sufficient to expose the visual decision surface to an Alexa-oriented inspector/host.  
**Actual:** The data-layer result and the visual surface are separate contracts. The tool must point to a UI resource and the host must fetch a `text/html;profile=mcp-app` resource, which required cross-referencing the base MCP protocol, Alexa+ guidance and the MCP Apps extension.  
**Severity:** **Medium** — no data corruption, but the difference between “tool works” and “tool renders” can cost significant implementation time.  
**Workaround:** Ripple implements a self-contained display-only MCP App and adds static/contract tests for the resource URI, MIME type, lifecycle and the invariant that the widget cannot call approval/execution.  
**Actionable suggestion:** Provide a single end-to-end Alexa+ sample that shows one tool declaration, `_meta.ui.resourceUri`, `resources/read`, exact MIME type, `ui/initialize`, tool-result delivery, theme/context updates and resize behavior in one repository.

**Evidence:** `docs/MCP_APP_REPAIR_CARD.md`, `docs/MCP_APP_EVIDENCE.md`.

## F3 — Add-on packaging had no single preflight for manifest + public media

**Date:** 2026-09-04  
**Task attempted:** Produce a judge-ready Alexa+ add-on package with manifest, required icons, carousel media, privacy/terms and a production MCP endpoint.  
**Steps taken:** Built the package, generated all required icon sizes and a 600×900 carousel, deployed the shared Docker image, then ran an independent remote media/package verifier against production.  
**Expected:** A successful deployment plus a locally valid package would make every manifest-referenced surface available in the deployed artifact.  
**Actual:** Railway reported deployment `SUCCESS`, but the independent runtime gate found that `addon-package/addon.json` had not been copied into the Docker image. The deployment lifecycle was healthy while the actual Alexa package contract was broken.  
**Severity:** **High** — the service looked deployed but a judge/onboarding flow relying on packaged metadata would fail.  
**Workaround:** Fixed the Docker image, added a CI invariant requiring the package directory, and created a remote gate that verifies the carousel dimensions/checksum/headers, privacy/terms content, all six icon dimensions and the canonical MCP URL.  
**Actionable suggestion:** Ship an official Alexa+ package preflight command that validates the manifest schema **and** resolves every referenced public asset/URL, checks required dimensions/content types, and reports missing packaged resources before onboarding or submission.

**Evidence:** `docs/ALEXA_REMOTE_EVIDENCE.md`, `scripts/alexa_store_media_smoke.py`, `scripts/alexa_addon_gate.py`.

## F4 — Least-privilege AWS credentials for a non-AWS PaaS runtime are operationally heavy

**Date:** 2026-09-05  
**Task attempted:** Keep Railway as the public MCP host while making Bedrock, DynamoDB and CloudWatch structural runtime dependencies under least privilege, without placing broad AWS credentials in source control.  
**Steps taken:** Evaluated the standard AWS external-workload paths, designed a CloudFormation-generated resource-scoped runtime policy, examined short-lived federation options, and built a credential lifecycle that can be created only after live AWS verification and revoked before teardown.  
**Expected:** A lightweight short-lived workload-identity path suitable for a small externally hosted container.  
**Actual:** The preferred non-AWS path, IAM Roles Anywhere, introduces CA/trust-anchor/workload-certificate lifecycle. The current Railway service does not expose a workload OIDC/JWT that can be exchanged directly with AWS STS, so there is no low-complexity short-lived bridge for this deployment topology.  
**Severity:** **High** — it does not block the product core, but it blocks the cleanest path from AWS-ready architecture to a live structural AWS runtime.  
**Workaround:** For the short-lived hackathon endpoint only, Ripple prepares a dedicated IAM user with **no console login**, exactly one access key, and only the stack-generated resource-scoped runtime policy. The secret is written once to a local `0600` transfer bundle, is never printed or committed, and teardown revokes the external principal even if the CloudFormation stack is already missing. The repository explicitly labels this as a temporary compromise rather than ideal long-term architecture.  
**Actionable suggestion:** Add a concise “external PaaS workload” guide comparing OIDC federation, Roles Anywhere and a bounded temporary IAM-user fallback, including threat model, rotation/teardown steps and copyable least-privilege examples for Bedrock + DynamoDB + CloudWatch.

**Evidence:** `docs/AWS_RUNTIME_CREDENTIALS.md`, `scripts/aws_railway_runtime_principal.sh`, `scripts/aws_teardown.sh`.

## F5 — Local Inspector documentation uses a JSON-only `Accept` request shape

**Date:** 2026-09-05  
**Task attempted:** Preflight Ripple against the request sequence published for the Alexa+ Add-on Local Inspector before spending time on partner-only onboarding.  
**Steps taken:** Compared the production MCP request validation with the current Local Inspector guide, reproduced the documented initialize/initialized/tool/resource sequence in an integration test, and built a standalone remote probe that uses the same request shape.  
**Expected:** The documented Inspector request headers would match the strict Streamable HTTP request shape already accepted by Ripple (`Accept: application/json, text/event-stream`).  
**Actual:** The Local Inspector guide's example sends `Accept: application/json`. Ripple's strict server therefore would have returned HTTP 406 before the Inspector reached authentication, tool discovery or the Repair Card. The guide also shows an older client protocol version in the initialization example, so the server must negotiate its supported `2025-11-25` version cleanly.  
**Severity:** **High** — a standards-focused MCP server could pass its own protocol suite and still fail the documented Alexa Inspector sequence at the first POST.  
**Workaround:** Ripple now accepts both the normal dual `Accept` form and JSON-only requests because the server emits JSON responses; SSE-only requests remain rejected. A dedicated test drives the documented older client-version request and proves negotiation to `2025-11-25`, `notifications/initialized`, tool listing and `ui://` resource discovery. A remote probe is included for the deployed service.  
**Actionable suggestion:** Align the Local Inspector request examples with the required MCP transport contract, or explicitly document that Inspector intentionally sends JSON-only `Accept` headers and that servers should tolerate that form. Also state clearly why the Inspector example advertises an older client protocol while Alexa+ submissions require MCP `2025-11-25` or newer.

**Evidence:** `tests/test_alexa_local_inspector_compat.py`, `scripts/alexa_local_inspector_probe.py`.
