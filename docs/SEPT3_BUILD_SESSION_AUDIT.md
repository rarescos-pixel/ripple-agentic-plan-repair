# Sep 3 Amazon Developer Hackathon build session — Ripple intelligence audit

## Source quality

This audit separates authoritative requirements from session intelligence.

**Tier A — authoritative:**

- official Devpost rules: `https://amazonappdev2026.devpost.com/rules`
- official Devpost resources: `https://amazonappdev2026.devpost.com/resources`
- official webinar page: `https://info.devpost.com/webinar-events/getting-started-with-building-apps-for-amazon-devices`
- official Alexa+ developer documentation.

**Tier B — session intelligence:** a detailed public Sep 4 recap of the Sep 3 Q&A/build session, reposted by Devpost on LinkedIn. It attributes the session to Amazon Developer hosts Chris Traganos / Moses Roth and summarizes Alexa+ Q&A takeaways. This is useful strategic evidence but is not treated as a verbatim transcript. Where it conflicts with the official rules, the rules win.

## What the Sep 3 session changes for Ripple

### 1. Alexa+ is being treated as an MCP ideation prize, not a certification contest

Session recap:

- Amazon called Alexa+ the **“MCP prize”** and an **“ideation project.”**
- Alexa+ add-ons are still emerging; Alexa+ not being live in a participant's country does not block the track.
- The official rules explicitly allow a self-hosted MCP server or a clearly labeled simulated Alexa+ experience.

**Ripple consequence:** stop treating official Alexa+ onboarding/certification as a prerequisite for a top Alexa+ submission. The public MCP server is the primary proof. Official Inspector/on-device evidence is useful bonus evidence only when accessible.

### 2. The recommended demo shape matches Ripple almost exactly

Session recap says the practical demo route is:

- build a web mockup of Alexa+;
- connect the MCP server to it;
- show the customer/agent conversation in the video.

Official rules separately confirm that a simulated Alexa+ experience is permitted and that judges may judge solely from text/images/video.

**Ripple consequence:** the highest-ROI remaining design task is the judge-facing simulated Alexa+ conversation backed by the real public MCP endpoint. Do not spend the first demo minute on protocol logs, Local Inspector, or certification screens.

### 3. Amazon is signaling transactional use cases

Session recap advises looking at:

- popular MCP servers;
- things customers want to **transact on without visiting a site**.

Official Alexa+ judging guidance calls purchasing, cross-service orchestration, cards/carousels, MCP Apps and stateful add-ons “creative” rather than “obvious.”

**Ripple fit:** excellent. Ripple's core value is exactly one customer statement replacing manual discovery/repair across multiple services. The submission should explicitly say **“repair the cascade without opening five apps/sites”**.

Do not overclaim: the current airline/ride/reservation/delivery/care providers are deterministic simulators, so the demo demonstrates the transaction/approval architecture, not live third-party purchases.

### 4. What Amazon says stands out maps directly to Ripple

Session recap says standout projects show:

1. a **customer talking to an agent**;
2. useful feedback such as a **rich card** or in-place purchase;
3. a real problem grounded in customer life;
4. a demo that actually runs.

Ripple status:

- customer → agent conversation: **implemented, but must dominate the final video**;
- rich card: **implemented as a real display-only MCP App Repair Card**;
- real-life problem: **strong travel-disruption wedge**; do not claim a personal anecdote unless true;
- working demo: **public MCP + remote smoke PASS**.

**Decision:** show the Repair Card as the immediate consequence of the spoken change, not as a technical artifact introduced later.

### 5. Product/engineering judges increase the value of coherence and evidence

The session recap says judges are mainly product and engineering leads from Amazon device teams. Official rules score:

- technical implementation;
- design;
- potential impact;
- quality of idea.

**Ripple consequence:** architecture depth only scores if the product story is obvious. Keep the first 60 seconds customer-facing, then use the deterministic approval/replay architecture as credibility evidence.

### 6. Friction logs are strategically important, not decorative

Session recap says product teams explicitly want the friction logs. Official rules go further: complete friction logs can add **up to 10%** to the final score after Stage 1 review.

Ripple already has five evidence-backed entries. Preserve them and prefer actionable, reproducible feedback over adding low-value quantity.

### 7. Alexa+ SDK/API updates may land during the hackathon

Session recap says Alexa+ SDK/API updates may be announced during the eight-week build window.

**Ripple consequence:** do not freeze platform assumptions until submission freeze. Monitor the official rules/resources/docs for changes, but only adopt an update if it materially improves eligibility, demo quality, or judge evidence without destabilizing the core.

### 8. $150 AWS promotional credits remove cost pressure from the AWS LIVE proof

The session recap mentions $150 AWS credits. The official rules confirm registered entrants may request **$150 AWS Promotional Credits** while supplies last, with the request form due **Oct 21, 2026 at 12pm PT**.

**Ripple consequence:** request the credits before AWS LIVE if not already requested. Cost remains audited, but the live proof should not be delayed to save a few dollars.

## What does NOT change

- Primary track remains **Alexa+**.
- Core product remains frozen: consequence graph + economic repair + exact approval + bounded execution + receipts.
- MCP remains the real runtime backbone.
- Repair Card remains display-only; do not add a direct widget approval path.
- Provider integrations remain truthfully labeled simulations.
- AWS stays structural and secondary to Alexa+; do not migrate the public MCP host just to add an AWS logo.
- Do not add AgentCore/Strands/Kiro merely because they appear in AWS Builder examples. Finish the existing Bedrock + DynamoDB + CloudWatch + IAM/Budget structural path first.

## Updated final-work priority

### P0 — judge-facing Alexa+ demo surface

Polish the simulated Alexa+ conversation backed by the public MCP server so the first 20 seconds show:

**user change → 5 affected commitments → $116 at risk → $42 repair → $74 preserved → exact approval**.

Label it accurately as a simulated Alexa+ experience backed by the real MCP server if no official client is available.

### P0 — AWS credits request

Request the official $150 AWS promotional credits if not already done.

### P0 — AWS LIVE proof

Finish the existing path:

**Nova benchmark → CloudFormation → Bedrock/DynamoDB/CloudWatch/Budget live verify → least-privilege Railway bridge → structural cutover → fresh-session replay proof.**

Do not add AWS services merely for scoring cosmetics.

### P1 — friction/product feedback freeze

Keep the five real friction entries, ensure every one has reproduction + expected/actual + workaround + actionable suggestion, and keep Product Feedback aligned with the same evidence.

### P1 — official Alexa Inspector/onboarding, if accessible

Treat official Inspector/on-device evidence as bonus proof, not a blocker. If access is unavailable, do not burn build time fighting a partner-access boundary; the rules and session explicitly support the simulated Alexa+ demo route.

### P1 — monitor platform updates

Watch official Alexa+/Devpost updates through the submission window and incorporate only concrete changes with measurable score gain.

### P2 — final video / Devpost

The final video must look like a customer using an agent, not an engineer inspecting infrastructure. Technical evidence supports the second half; it does not lead the story.

## Competitive interpretation

This session materially improves Ripple's position because Amazon verbally emphasized exactly the class of experience Ripple already implements:

**agent conversation + cross-service transaction intent + rich feedback + a real problem + a working demo.**

The remaining risk is therefore not product-market/track fit. It is execution quality in the final demo and closing the AWS LIVE evidence gap without distracting from Alexa+.
