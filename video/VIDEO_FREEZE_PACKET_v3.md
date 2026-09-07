# Ripple VIDEO FREEZE PACKET — v3

Status: VIDEO-READY EVIDENCE PACKET for `submission/video-pipeline-v3-work`.

This packet freezes the source/runtime/evidence claims allowed in the Winner Cut v3. It does not modify the technical runtime.

## 1. Build identity

- VIDEO-READY git SHA: `c6766c5919ea903530a8da2d526d64a49b7f0578`
- branch/ref for technical source: `main`
- commit message: `Trigger canonical exact-SHA proof refresh`
- live URL: `https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws`
- canonical MCP URL: `https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws/mcp`
- canonical judge demo: `https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws/demo`
- deployment identity: ECR digest `sha256:1a2382fbdfca7d4a53bce687cb09094091c36107353838aae8b8a1116719bb54`; ECS task definition `arn:aws:ecs:eu-central-1:873363353521:task-definition/ripple-canonical-custom:7`
- release proof workflow: `34152287142` — SUCCESS
- quality gate workflow: `34152287221` — SUCCESS
- frozen at: 2026-09-07 Europe/Bucharest

## 2. Golden scenario — exact verified state

### User change
- exact user utterance/input used in the public/demo narrative: `Our flight home was cancelled. We’ll land tomorrow at six.`
- previous state: pre-existing downstream commitments from the deterministic golden fixture
- new state: arrival shifted to tomorrow 18:00

### Dependency analysis
- exact number of impacts: **5**
- human-facing impact categories used in the judge narrative: ride, dinner reservation, grocery delivery, pet-care window, tomorrow's meeting

### Economics
- total direct avoidable loss / at risk: **$116**
- added repair cost: **$42**
- net direct cash preserved: **$74**
- evidence source: live `/demo/api/evidence`, scenario `golden_flight_cascade`; final release proof workflow `34152287142`

### Approval
- exact approval behavior: approval binds to the exact proposed plan content/scope/cost and snapshot state
- content drift invalidates approval and forces reapproval
- preview writes: **0**
- approval writes: **0**

### Execution
- exact number of actions: **5**
- exact number of authoritative receipts: **5**
- expected replay behavior: all five actions deduplicate
- authoritative unique-write count on fresh-session replay: **5 → 5**
- new provider writes expected on replay: **0**

### Interruption recovery
- persisted receipts before resume: **2**
- deduplicated on resume: **2**
- new writes on resume: **3**
- unique writes total: **5**
- final status: `executed`

## 3. Generality scenario — exact verified state

Event Operations deterministic scenario:

- impacts: **5**
- avoidable loss / at risk: **$5,800**
- repair cost: **$620**
- net preserved: **$5,180**
- external people: **8**
- selected AV operation: `move_av_delivery`
- top impact labels: Catering service window; AV equipment delivery; Security staffing coverage

Use this only as a fast generality proof. Do not present the fixture amounts as market prices, TAM, or measured ROI.

## 4. Capture path

Required capture order:

1. Open the real judge demo from the frozen AWS build.
2. Establish/reset the golden scenario state.
3. Capture change → impacts → economics → exact approval → execution → receipts in one coherent run.
4. Capture replay/fresh-session dedup proof with observable `5/5 deduplicated`, `writes 5 → 5`, `0 new provider writes`.
5. Capture a separate short Event Ops evidence state only if it remains useful for generality.

Preferred automation path remains deterministic browser capture (Playwright/Chromium) according to `video/CAPTURE_SPEC.md`.

## 5. VERIFIED platform claims

- public demo: **VERIFIED WORKING**
- public `/readyz`: **VERIFIED WORKING**
- current live source revision: **VERIFIED `c6766c5919ea903530a8da2d526d64a49b7f0578`**
- structural AWS runtime: **VERIFIED WORKING**
- AWS components reported live: **DynamoDB + Bedrock + CloudWatch**
- ECS Express/Fargate canonical public runtime: **VERIFIED WORKING**
- MCP 2025-11-25 Streamable HTTP: **VERIFIED WORKING**
- authenticated MCP smoke: **PASS**
- OAuth refresh without resource: **PASS**
- wrong OAuth resource: **rejected as expected**
- Amazon Bedrock / Nova 2 Lite changed-fact normalization: **PASS**
- DynamoDB durable fresh-session replay: **PASS**
- CloudWatch redacted trace evidence: **VERIFIED in final release proof**
- Alexa+ simulated experience backed by real public MCP: **AVAILABLE / allowed claim when labelled as simulation**
- official Alexa+ production-client session: **NOT CLAIMED**
- one bounded real GitHub Issues provider proof: **VERIFIED historical/frozen project capability; use only if needed and evidenced**

## 6. Claims explicitly forbidden in the video

- Do not claim airline, ride, restaurant, grocery, pet-care, or calendar integrations are production provider transactions.
- Do not claim the deterministic fixture dollar values are live prices or guaranteed ROI.
- Do not claim actual Alexa+ production-client use unless separately exercised and recorded from an official client.
- Do not imply BTS disruption counts equal Ripple TAM, user count, conversion, or repair-event incidence.
- Do not present Railway as the current canonical runtime.
- Do not present simulated UI as Amazon certification or official Alexa Inspector evidence.
- Do not expose AWS account identifiers, SSM names containing secret context, tokens, cookies, authorization codes, passwords, or private console state in footage.

## 7. Evidence / release facts allowed for judge-facing use

- exact frozen source SHA: `c6766c5919ea903530a8da2d526d64a49b7f0578`
- ECR immutable digest: `sha256:1a2382fbdfca7d4a53bce687cb09094091c36107353838aae8b8a1116719bb54`
- ECS task definition: `ripple-canonical-custom:7`
- public `/readyz` exact-SHA stability: **6 consecutive PASS**
- public judge evidence: **7/7 for 6 consecutive reads**
- golden: **5 impacts / $116 at risk / $42 repair / $74 preserved / 5 actions / 5 writes after approval**
- fresh-session replay: **5/5 deduplicated; authoritative writes 5 → 5; 0 new provider writes**
- interruption recovery: **2 persisted → 2 dedup + 3 new → 5 unique**
- authenticated MCP smoke: **PASS**
- Bedrock normalization: **PASS**
- temporary deployment bootstrap IAM policy: **deleted successfully after release proof**

## 8. UI / capture freeze

- target viewport: **1920x1080**
- aspect ratio: **16:9**
- language: **English**
- visual source priority: real judge UI first; motion graphics only to clarify verified state
- reset procedure: deterministic golden-scenario reset before each full take
- no stale receipts presented as new
- no preapproval write may occur
- no sensitive browser/auth data visible
- no accidental browser chrome/cursor wandering unless interaction requires it

## 9. Final pre-capture gate

- [x] exact source revision identified
- [x] deployed build matches source revision (verified with fresh cache-busted `/readyz`)
- [x] golden public evidence currently 7/7 (verified with fresh cache-busted `/demo/api/evidence`)
- [x] zero writes before approval proven in release smoke/evidence
- [x] receipts proven after approval
- [x] replay/deduplication proven
- [x] economics values independently reconciled to live evidence
- [x] current AWS/MCP platform claims have release evidence
- [x] forbidden claims documented
- [ ] deterministic capture/reset script executed for this video freeze
- [ ] raw full-flow take captured and hashed
- [ ] master video validated and cold-reviewed

VIDEO SOURCE/RUNTIME STATUS: **READY FOR CAPTURE**.

This does **not** mean the video itself is GOOD/READY/SUBMISSION-READY. Those statuses remain controlled by `VIDEO_ACCEPTANCE_STANDARD_v1.1.md` and `VIDEO_SCORECARD_v1.1.template.md`.