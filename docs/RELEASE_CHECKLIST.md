# Release / Submission Checklist — v1.2

## Verified local quality
- [x] 43/43 full tests PASS.
- [x] 12/12 MCP + OAuth protocol tests PASS.
- [x] 6/6 adversarial scenarios PASS.
- [x] release gate PASS.
- [x] exact approval / zero-write preview / replay idempotency.

## Verified public MCP
- [x] public HTTPS endpoint deployed on Railway.
- [x] `/readyz` production health gate PASS.
- [x] OAuth protected-resource + authorization-server discovery.
- [x] service client credentials and user authorization-code + PKCE S256.
- [x] independent remote smoke from a second Railway container.
- [x] `tools/list` exposes exactly five bounded Ripple tools.
- [x] remote preview = 5 impacts / 0 writes.
- [x] remote approval = 0 writes.
- [x] remote execution = 5 receipts / 5 unique writes.
- [x] remote replay = 5/5 deduplicated / still 5 unique writes.
- [x] server-side proxy/runtime logs corroborate the remote flow.

## Repository / Open Source
- [x] public GitHub repository exists.
- [x] MIT license visible.
- [x] source, tests, judge packet and reproducible smoke script present.
- [ ] public GitHub Actions quality gate green on the complete repository snapshot.

## Still required before final submission
- [ ] actual Alexa+ onboarding/client connection if available to contestant account.
- [ ] public video <3 minutes.
- [ ] final Devpost copy reconciled against runtime evidence.
- [ ] product/API feedback for every Amazon tool actually used.

## AWS Builder — only if pursued
- [ ] real Bedrock call.
- [ ] Lambda deployed/exercised.
- [ ] DynamoDB restart-durable persistence.
- [ ] CloudWatch trace evidence.
- [ ] least-privilege IAM and budget alarm.
