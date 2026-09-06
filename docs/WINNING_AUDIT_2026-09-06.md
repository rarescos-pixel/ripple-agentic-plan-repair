# Ripple — winning audit — 2026-09-06

Purpose: adversarial audit against the current Amazon Developer Hackathon rules, publicly discoverable 2026 Alexa+ competitors, and recurring traits of prior Amazon Alexa challenge winners. This is an execution document, not marketing copy.

## Evidence boundary

- Official rules: https://amazonappdev2026.devpost.com/rules
- Current Devpost project gallery is not published as of this audit. Therefore the competitor set below is **not exhaustive**. Do not claim Ripple has been compared with every submission.
- Competitor claims below are limited to public repositories/pages inspected on 2026-09-06.
- Video work is explicitly **LOCKED** until the project owner starts that phase.

## 1. Official requirement compliance

| Requirement | State | Ripple evidence / action |
|---|---|---|
| Working Alexa+ project | VERIFIED | Public self-hosted MCP service plus clearly labelled simulated Alexa+ judge UI. |
| MCP >= 2025-11-25 | VERIFIED | Server pins `2025-11-25`; conformance tests run explicitly in CI. |
| Streamable HTTP | VERIFIED | Public `/mcp`; independent remote authenticated smoke. |
| Required technology actually called at runtime | VERIFIED | MCP runtime is the project entry surface, not a README-only claim. |
| Public GitHub repo | VERIFIED | Public repository. |
| Open-source license visible | VERIFIED | MIT license. Recheck Devpost/About visibility at submission freeze. |
| Source, assets, setup/run instructions | VERIFIED | Repo contains runtime, Alexa assets/package, infrastructure, scripts and README. |
| Project functioning in demo | CURRENT | Public judge demo is functioning and independently smoke-tested. Final submission video remains LOCKED/not recorded. |
| Demo on intended platform | CURRENT | Rules explicitly allow a clearly-labelled simulated Alexa+ web experience. Official Alexa+ client footage is optional upside, not a validity dependency. |
| Demo video < 3 minutes, public YouTube/Vimeo, English | NOT STARTED / VIDEO LOCKED | Must be completed with owner. Judges need not watch beyond 3:00. |
| Text project description | CURRENT | Repo contains judge-facing copy; final Devpost field freeze remains. |
| Product feedback for every Amazon tool/API/service used | CURRENT | Product feedback packet exists. Must be reconciled after final AWS state. |
| Primary track identified | VERIFIED | Alexa+. |
| AWS Builder services described and documented | CURRENT | DynamoDB + Bedrock live evidence exists; CloudWatch Logs live proof is being closed. Claim only after full gate PASS. |
| Open Source mini exact fields | VERIFIED / FREEZE PENDING | New MIT repo + representative PR/contribution packet exist. Final URLs/user/description must be copied exactly to Devpost. |
| Third-party integration authorization | VERIFIED FOR CURRENT DEMO | Provider transactions are deterministic simulations and labelled as such. No unlicensed production provider claims. |
| Original work / hackathon-window provenance | VERIFIED | Repo and contribution history are in-window. Preserve commit history. |
| Free and accessible through judging | CURRENT | Public Railway runtime must remain available through 2026-11-20 12:00 PT. |
| English submission materials | VERIFIED for repo; video pending | Docs/UI are English. |
| No substantive post-deadline edits | FUTURE CONTROL | Freeze exact final SHA and submission packet before 2026-10-23 12:00 PT. |
| Friction log optional bonus | VERIFIED / MAXIMIZE | Existing real entries satisfy required fields. Final review for truthful completeness; no fabricated entries. |

## 2. Stage-2 judging audit

The four criteria are equally weighted. Tie-break starts with Technical Implementation.

### Technical Implementation — current target: 9+/10 before final freeze

Verified strengths:
- real public MCP 2025-11-25 Streamable HTTP;
- OAuth protected-resource / authorization-server metadata, authorization-code + PKCE, refresh and service credentials;
- five bounded tools with annotations;
- MCP App Repair Card resource;
- deterministic dependency traversal and economic planner;
- exact content-hash approval binding;
- no-write proposal phase;
- provider preflight;
- durable idempotency/receipts and interruption replay;
- CI, remote smoke, Alexa package/media gates, Local Inspector compatibility tests;
- GitHub OIDC to AWS without static AWS keys;
- live DynamoDB durability/idempotency evidence;
- live Amazon Nova 2 Lite invocation evidence.

Remaining P0/P1:
1. Prove the **actual CloudWatch Logs trace path**, not an unrelated custom metric.
2. Cut canonical Railway runtime to the final structural AWS profile only after DynamoDB + Bedrock + CloudWatch all pass.
3. Prove the final exact source revision publicly after cutover.
4. Keep provider simulation disclosures explicit; never imply airline/calendar/etc production writes.

### Design — current target: 9/10 before video

Strengths:
- one changed fact → one money-first decision surface;
- customer sees impact, cost, preserved value and notification scope before approval;
- voice/card parity;
- exact approval and receipts are understandable trust primitives;
- mobile-friendly public judge demo;
- simulated Alexa+ boundary is labelled rather than disguised.

Gap:
- economic selection is technically strong but the customer/judge cannot always see **why this repair beats a cheaper alternative**. Add deterministic, non-LLM optimization evidence only when mechanically provable.
- final perceived polish will depend heavily on the owner-led video phase; do not touch video before unlock.

### Potential Impact — current target: 9+/10

Strengths:
- direct measurable outcome rather than generic productivity: `$116 → $42 → $74` in consumer fixture;
- separate Event Operations fixture: `$5,800 → $620 → $5,180`;
- core primitive is consequence repair, not a travel-specific FAQ;
- clear extensions to travel concierge, corporate travel, hospitality recovery, event operations, insurance and executive assistance.

Gap:
- canonical live judge path is travel-first; cross-domain generality exists in executable evidence but is less visible than the travel demo. Preserve one narrow hero scenario, but keep a concise cross-domain proof available in technical evidence.
- avoid market-size claims without sources. Specific customer economics are stronger than inflated TAM language.

### Quality of Idea — current target: 9.5/10

Official Alexa+ rules explicitly contrast basic Q&A/API wrappers with autonomous cross-service workflows, state across sessions, rich media/MCP Apps and agent skills. Ripple already sits in the creative archetype: it reasons over a dependency graph, orchestrates multiple service types, surfaces a real MCP App, uses state, and takes bounded action after exact approval.

Primary differentiator to protect:
> Ripple does not merely automate tasks. It prices the downstream consequence set, chooses the safe repair that preserves the most net value, binds authority to one exact plan, and proves every effect with receipts.

Do not dilute this with unrelated features.

## 3. Public 2026 competitor audit

### Caremesh MCP — `Darlington6/caremesh-mcp`

High-risk competitor.

Public strengths:
- strong human problem: family/caregiver coordination;
- self-hosted MCP 2025-11-25;
- live deployment on Amazon ECS Express Mode;
- real DynamoDB and Bedrock;
- ten tools across check-ins, medication, tasks, household summaries/alerts;
- multiple household members and habitual/daily use;
- CI, Docker, AWS-native deployment story;
- targets Alexa+ + AWS Builder + Open Source.

Where Ripple is stronger:
- full OAuth/PKCE rather than a plain bearer-token surface;
- exact approval binding;
- economic optimization and counterfactual value;
- bounded execution, authoritative receipts and replay safety;
- MCP App decision surface;
- more rigorous safety/remote evidence.

Where Caremesh exposes a Ripple risk:
- it is easier to understand as an everyday habit and has a stronger persistent end-user-data story;
- AWS is visibly part of the live hosting architecture.

Response: do **not** imitate caregiving or add ten tools. Close real AWS structural proof, make durable recovery explicit, and make the human value loop instantly legible.

### Opportunity Radar — `kevin9327/opportunity-radar`

Serious competitor on trust and real-data usefulness.

Public strengths:
- six useful tools over real `grants.gov` data;
- structural honesty gates rather than prompt-only claims;
- explicit source-unavailable / unknown / missing-deadline behavior;
- Bedrock/local ranking with factual dollars/deadlines reattached from source data;
- scheduled weekly live-source CI;
- zero-key public data source and privacy-aware local ranking.

Where Ripple is stronger:
- substantially deeper agentic execution and multi-service repair;
- exact approval and side-effect safety;
- MCP App/rich decision surface;
- durable receipts/replay;
- quantified repair economics instead of ranking information only.

Lesson: every uncertainty in Ripple must remain explicit. Never fabricate a provider state or a saved dollar amount.

### Ops Concierge — `tkomane/ops-concierge`

UX/storytelling competitor.

Public strengths observed:
- relatable household scenarios;
- visible tool timeline and consumer-oriented web experience;
- mocked integrations are clearly labelled;
- lightweight/static deployment makes the demo very accessible.

Where Ripple is stronger:
- real public authenticated MCP;
- deeper protocol/security implementation;
- economic optimizer;
- exact approval + receipts + replay;
- real AWS evidence.

Lesson: technical depth wins only if the first customer loop is at least as easy to understand as the simpler consumer demos.

## 4. Historical Amazon Alexa winner pattern

Across official Amazon winner announcements (2017–2021), recurring winning traits are:

1. **Native voice fit beats complexity for its own sake.** Smart Elephant and Mommy-gram were memorable because speaking was the natural input at the exact moment of need.
2. **Specific human loop.** Kids Court solved sibling disputes; Mommy-gram closed parent/child communication; Art Museum enabled natural exploration; Fitnesscoach built a repeated workout loop.
3. **Habit/repeat value.** Amazon repeatedly praised experiences customers return to.
4. **Multimodal polish when useful.** Loop It and later challenges rewarded visuals/touch/audio that extended, rather than replaced, voice.
5. **Delight and coherent design.** Prior judging emphasized creativity, voice-first UX, technical implementation and customer engagement/feedback.
6. **Demo quality matters.** Amazon explicitly noted exceptionally polished demo videos in past finalist sets.

Implication for Ripple:
- engineering depth is already beyond many historical winners;
- the remaining risk is not “need more features”; it is failure to convert that depth into one unforgettable, obvious customer outcome;
- the hero sentence and money-first cascade are therefore strategic assets, not temporary copy.

## 5. Winner-gap backlog

Priority order is based on score gain / cost / risk, not feature count.

### P0 — must close

- [ ] CloudWatch **Logs** live trace PASS using the same structured/redacted trace shape as runtime.
- [ ] Structural AWS canonical runtime PASS: DynamoDB + Bedrock + CloudWatch together, fail-closed on partial config.
- [ ] Exact-revision Railway deployment and independent public judge smoke on final technical SHA.
- [ ] Reconcile README, rubric map, AWS status, product feedback and submission packet to the final observed state.
- [ ] Full competition-compliance freeze: no missing mandatory field.

### P1 — high score gain, bounded risk

- [ ] Add deterministic optimization evidence: selected repair vs best visible safe alternative, net-value delta; never invent reasons hidden by policy.
- [ ] Make durable/restart semantics judge-verifiable at the MCP/session boundary, not only executor unit level.
- [ ] Keep cross-domain Event Operations proof easy to discover without weakening the narrow golden customer story.
- [ ] Visual audit public judge UI on mobile/desktop; fix only concrete defects.

### P2 — only if evidence shows score gain

- [ ] Official Alexa+ client/Inspector footage or onboarding if accessible cleanly. Simulation remains rules-valid; do not create a manual-work critical path.
- [ ] One real external provider adapter only if it can be legal, stable, cheap and independently testable. Do not trade reliability for a decorative “real API” badge.
- [ ] Additional AWS services only if they become structurally necessary. No AgentCore/Step Functions/vector DB/always-on compute for rubric theatre.

## 6. Explicit non-goals

- No feature-count race with competitors.
- No multi-agent architecture unless the problem actually requires it.
- No fake production provider transactions.
- No decorative AWS service additions.
- No weakening exact approval to make the demo faster.
- No video changes until the owner explicitly unlocks the video phase.

## Win condition

The technical build is ready to freeze only when:

1. every mandatory competition requirement is VERIFIED or a clearly scheduled human-only submission step;
2. all current CI/release/remote gates pass on one exact SHA;
3. public Railway points to that exact SHA;
4. AWS structural evidence is real and current;
5. no judge-facing claim exceeds observed evidence;
6. the golden customer loop remains simple enough to understand in seconds;
7. the repository contains no known P0 defect or stale contradictory evidence.
