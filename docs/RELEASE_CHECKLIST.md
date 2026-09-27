# Release / Submission Checklist — winner-build

## Core / safety — VERIFIED
- [x] full repository test suite PASS on current main lineage.
- [x] MCP 2025-11-25 protocol conformance PASS.
- [x] Alexa request-shape compatibility PASS.
- [x] exact approval / zero-write preview / zero-write approval.
- [x] deterministic economic optimization.
- [x] authoritative receipts and idempotent replay.
- [x] exact approved-plan recovery across process/session restart.
- [x] adversarial/failure-truth matrix PASS.
- [x] money-first Repair Card + deterministic rationale + receipt timeline.

## Public MCP / AWS canonical runtime — VERIFIED
- [x] public HTTPS endpoint deployed on Amazon ECS Express Mode / Fargate.
- [x] `/readyz` reports `aws-structural` and the exact deployed source revision.
- [x] OAuth protected-resource + authorization-server discovery.
- [x] service client credentials and user authorization-code + PKCE S256.
- [x] `tools/list` exposes exactly five bounded Ripple tools.
- [x] remote preview = 5 impacts / 0 writes.
- [x] remote approval = 0 writes.
- [x] remote execution = 5 authoritative receipts / 5 unique writes.
- [x] fresh-session replay = 5/5 deduplicated / authoritative unique writes remain 5 → 5.
- [x] Bedrock / Nova 2 Lite live normalization.
- [x] DynamoDB durable proposal/approval/idempotency/receipt state.
- [x] CloudWatch redacted structured runtime traces.
- [x] ECS task-role runtime identity; no static AWS application keys.
- [x] GitHub OIDC bounded deployment/proof identity.

Historical Railway deployments remain audit evidence only. No Railway deployment is required for the current release or submission freeze.

## Real external provider — VERIFIED
- [x] bounded GitHub Issues provider adapter.
- [x] allowlisted repository/issue target.
- [x] reversible zero-cost write.
- [x] provider readback PASS.
- [x] exact replay dedup PASS.
- [x] exact restore PASS.
- [x] fixture restored to baseline after proof.

Travel-world airline/ride/reservation/delivery/pet-care/calendar adapters remain explicitly simulated.

## AWS Builder — CANONICAL STRUCTURAL LIVE VERIFIED
- [x] GitHub OIDC assume-role PASS.
- [x] real Amazon Nova 2 Lite inference PASS.
- [x] DynamoDB receipt write/readback PASS.
- [x] DynamoDB replay conditional-write rejection PASS.
- [x] CloudWatch Logs structured event write + readback PASS.
- [x] aggregate `AWS_DIRECT_LIVE_EVIDENCE=PASS`.
- [x] canonical public ECS runtime uses Bedrock + DynamoDB + CloudWatch structurally.
- [x] least-privilege task-role runtime; no committed static AWS keys.
- [x] budget/anomaly guardrails configured.
- [x] deterministic cost benchmark documented.

## Repository / Open Source — VERIFIED
- [x] public GitHub repository.
- [x] MIT license visible.
- [x] source, tests, evidence and reproducible probes present.
- [x] Open Source mini-challenge packet present.
- [x] representative contribution PR #22 documented.
- [x] public GitHub Actions quality gate green on current main lineage.

## Judge packet / submission surfaces
- [x] README evidence-bounded and AWS-canonical.
- [x] `SUBMISSION_DRAFT.md` reconciled to AWS canonical runtime, direct AWS live evidence and real-provider proof.
- [x] `PRODUCT_FEEDBACK.md` reconciled to observed AWS results.
- [x] `MASTER.md` canonical state reconciled.
- [x] `RUBRIC_MAP.md` current.
- [x] `JUDGE_PACKET.md` and `JUDGE_RUNBOOK.md` point only to the canonical AWS runtime.
- [x] friction log packet complete.
- [x] adversarial matrix + cost benchmark linked.
- [ ] final Devpost fields copied/frozen after all technical changes stop.
- [ ] final public URL/SHA/evidence reconciliation after the **last** merge.

## Alexa+ optional upside
- [ ] official Alexa+ onboarding/client/Inspector evidence if accessible without creating a manual critical path.

Rules-valid simulated Alexa+ experience backed by the real public MCP remains the baseline and is not blocked by official-client access.

## VIDEO — LOCKED
- [ ] public video <3 minutes.
- [ ] English judge-first narration/captions as required.
- [ ] final recorded demo uses the exact frozen public build.

**Do not start, rewrite, generate, edit or record video material without Rareș explicitly present and unlocking the video phase.**

## Final freeze sequence
1. finish any remaining score-positive non-video work;
2. merge final technical/docs state;
3. require main Quality Gate PASS;
4. build the final Git SHA to an immutable ECR digest;
5. converge ECS Express Mode / Fargate to that exact task definition;
6. require repeated `/readyz` exact-SHA PASS;
7. require authenticated MCP/OAuth smoke PASS;
8. require live Bedrock normalization + DynamoDB fresh-session replay with 5/5 deduplicated and authoritative writes unchanged;
9. require CloudWatch execution evidence and ECR digest readback;
10. freeze technical repository and judge packet;
11. STOP and begin VIDEO only with owner;
12. final Devpost entry + compliance audit; preserve the AWS public runtime through judging.
