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

## Public MCP / Railway — VERIFIED
- [x] public HTTPS endpoint deployed on Railway.
- [x] `/readyz` production health gate PASS.
- [x] OAuth protected-resource + authorization-server discovery.
- [x] service client credentials and user authorization-code + PKCE S256.
- [x] `tools/list` exposes exactly five bounded Ripple tools.
- [x] remote preview = 5 impacts / 0 writes.
- [x] remote approval = 0 writes.
- [x] remote execution = 5 receipts / 5 unique writes.
- [x] remote replay = 5/5 deduplicated / still 5 unique writes.
- [x] exact-revision production deploy on `58898530b40564e1b0025db4ac8ea7d2f9249817` SUCCESS.
- [x] independent `Ripple Railway production proof` for that exact source SHA SUCCESS.

Any later merge after that SHA invalidates the “final exact SHA” label and requires one final redeploy + proof before technical freeze.

## Real external provider — VERIFIED
- [x] bounded GitHub Issues provider adapter.
- [x] allowlisted repository/issue target.
- [x] reversible zero-cost write.
- [x] provider readback PASS.
- [x] exact replay dedup PASS.
- [x] exact restore PASS.
- [x] fixture restored to baseline after proof.

Travel-world airline/ride/reservation/delivery/pet-care/calendar adapters remain explicitly simulated.

## AWS Builder — DIRECT STRUCTURAL LIVE VERIFIED
- [x] GitHub OIDC assume-role PASS.
- [x] real Amazon Nova 2 Lite inference PASS.
- [x] DynamoDB receipt write/readback PASS.
- [x] DynamoDB replay conditional-write rejection PASS.
- [x] CloudWatch Logs structured event write + readback PASS.
- [x] aggregate `AWS_DIRECT_LIVE_EVIDENCE=PASS`.
- [x] least-privilege / no committed static AWS keys for evidence path.
- [x] $5 monthly budget guard + $5 anomaly threshold configured.
- [x] deterministic cost benchmark documented.
- [ ] canonical Railway process configured to use Bedrock + DynamoDB + CloudWatch for every public request.

The unchecked Railway AWS-runtime cutover is **not** permission to move AWS secrets through chat or weaken the working public service. Proceed only through a credential-safe identity/transfer route with bounded regression risk.

## Repository / Open Source — VERIFIED
- [x] public GitHub repository.
- [x] MIT license visible.
- [x] source, tests, evidence and reproducible probes present.
- [x] Open Source mini-challenge packet present.
- [x] representative contribution PR #22 documented.
- [x] public GitHub Actions quality gate green on current main lineage.

## Judge packet / submission surfaces
- [x] README evidence-bounded.
- [x] `SUBMISSION_DRAFT.md` reconciled to direct AWS live evidence and real-provider proof.
- [x] `PRODUCT_FEEDBACK.md` reconciled to observed AWS results.
- [x] `MASTER.md` canonical state reconciled.
- [x] `RUBRIC_MAP.md` current.
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
2. decide whether credential-safe Railway AWS-backend cutover is worth the remaining risk;
3. merge final technical/docs state;
4. set `RIPPLE_RELEASE_SHA` to the final main SHA to force exact Railway deployment;
5. require Railway deployment SUCCESS for that SHA;
6. require independent `Ripple Railway production proof` PASS for the same SHA;
7. require main Quality Gate PASS;
8. freeze technical repository and judge packet;
9. STOP and begin VIDEO only with owner;
10. final Devpost entry + compliance audit; preserve public runtime through judging.
