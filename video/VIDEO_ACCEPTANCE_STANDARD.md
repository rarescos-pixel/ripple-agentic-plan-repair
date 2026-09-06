# Ripple Video Acceptance Standard v1.0

Status: CANONICAL QUALITY GATE for the submission video.

This document is the authority for deciding whether a Ripple video is merely renderable, presentable, GOOD, or READY.

**Rule:** organizer requirements are the base layer. Winner/concurrent benchmarks are an additional stricter layer. A video may not be called **GOOD**, **READY**, **FINAL**, or **SUBMISSION-READY** unless every mandatory criterion below is PASS with observable evidence.

Allowed criterion states: `UNKNOWN`, `FAIL`, `PASS`, `N/A-EXPLAINED`.

`N/A-EXPLAINED` is allowed only where the criterion is genuinely conditional and the explanation is written in the scorecard. It may not be used to bypass a hard organizer requirement.

---

# LAYER 0 — OFFICIAL ORGANIZER COMPLIANCE (HARD GATE)

Source of truth: current Build, Ship, Shape: Amazon Developer Hackathon rules and current Alexa+ track requirements.

If any Layer 0 item is FAIL or UNKNOWN, the video is **NOT READY**, regardless of production quality.

## O1. Duration
- [ ] Final demo is **less than 3:00**.
- [ ] No essential evidence occurs after 3:00.
- [ ] Target master remains approximately **2:15–2:25** unless evidence density justifies a different duration.

## O2. Public delivery
- [ ] Final video is publicly visible on YouTube or Vimeo at submission time.
- [ ] Link works from an unauthenticated context.

## O3. English
- [ ] Spoken narration/dialogue is English or has accurate English translation/subtitles.
- [ ] On-screen evidence needed for judging is understandable in English.

## O4. Project actually functioning
- [ ] The video shows Ripple **functioning**, not only mockups, slides, architecture diagrams, or claims.
- [ ] Functionality shown maps to the source code and the exact VIDEO FREEZE build.
- [ ] The core demonstrated behavior is reproducible from the frozen build.

## O5. Intended platform / Alexa+ path
- [ ] The video clearly shows the project working through the submission path actually claimed for Alexa+.
- [ ] If submitting the self-hosted MCP path, evidence is consistent with the required MCP version and Streamable HTTP runtime used by the frozen build.
- [ ] If any simulated Alexa+ surface is shown, it is explicitly treated as a simulation where necessary and its source exists in the repository.
- [ ] No simulated surface is presented as official Alexa+ certification or Inspector evidence unless independently verified.

## O6. Track technology is real, not decorative
- [ ] Required technology is actually used at runtime in the submitted project path, not merely named in narration or README.
- [ ] The video does not imply a platform integration that the code does not execute.

## O7. IP / licensing
- [ ] No third-party trademark, copyrighted music, footage, imagery, voice, or other protected material appears without permission or a valid license.
- [ ] Every non-original asset used in the master has a recorded source/license in `video/ASSET_MANIFEST.csv`.
- [ ] Generated assets have a documented generator/source and permitted usage terms.

## O8. Judge-alone viability
- [ ] The video is sufficient for a judge who never runs the repository.
- [ ] It communicates the problem, the idea, actual functionality, and why it matters without requiring external explanation.

---

# LAYER 1 — OFFICIAL JUDGING CRITERIA TRANSLATED INTO VIDEO OBLIGATIONS

The current four judging criteria are equally weighted. The film must make a strong case for **all four**; the video may not assume the written Devpost page will compensate for a missing dimension.

## J1. Tech Implementation
Mandatory evidence:
- [ ] A real end-to-end flow is visible.
- [ ] At least one genuinely difficult technical property is **shown**, not merely narrated.
- [ ] Approval/execution boundaries are visually understandable.
- [ ] Receipts/output evidence are visible.
- [ ] Replay/idempotence is demonstrated if retained as a claim.
- [ ] Platform/runtime claims shown on screen are VERIFIED at VIDEO FREEZE.
- [ ] The film contains no technology-logo wall used as a substitute for proof.

**Ripple target:** the judge should leave with evidence that Ripple is an operating agentic system, not a scripted concept video.

## J2. Design
Mandatory evidence:
- [ ] The interaction model is understandable without explanation of internal implementation.
- [ ] The customer knows what changed, what Ripple proposes, what requires approval, and what happened afterward.
- [ ] The film shows one coherent product experience rather than disconnected features.
- [ ] Visual hierarchy makes the user action, Ripple reasoning/output, economic consequence, approval, and result immediately distinguishable.
- [ ] UI text is readable at normal laptop/mobile video playback size.
- [ ] Audio supports interaction and comprehension rather than merely decorating the edit.

## J3. Potential Impact
Mandatory evidence:
- [ ] A specific customer pain is apparent in the opening sequence.
- [ ] Consequences are concrete, not generic productivity claims.
- [ ] Economic/customer value is quantified where verified.
- [ ] The film shows why the solution matters beyond a hackathon demo.
- [ ] If a second scenario is retained, its sole job is to prove generality/scalability quickly; it may not become a second full demo.

## J4. Quality of the Idea
Mandatory evidence:
- [ ] The differentiator is visible within the opening sequence.
- [ ] The film makes clear that Ripple is not merely chat, reminders, notifications, or a single API call.
- [ ] The central idea is dependency-aware **plan repair after change**.
- [ ] The core concept can be recalled in one sentence after viewing.
- [ ] The chosen use of Alexa+/agentic tooling feels native to the problem rather than bolted on for eligibility.

---

# LAYER 2 — WINNER / COMPETITOR BENCHMARK GATE

Derived from scene-by-scene review of available winning Amazon/Alexa demos and inspection of a current 2026 competitor. This layer is deliberately stricter than the rules.

Reference set used for v1.0:
- **Art Museum** — Alexa Conversations Grand Prize. Full video reviewed scene-by-scene (~1:51).
- **Voice Blast** — Beyond Voice Grand Prize. Full video reviewed scene-by-scene (3:00).
- **Fitnesscoach** — In-Skill Purchasing Grand Prize. Historical winning project and production-stack evidence reviewed; detailed frame analysis unavailable because the historical video is currently private.
- **Kids Court** — historical Amazon winner described by Amazon as using a teaser-style demo; used only for the principle that polish/teaser treatment can work when tied to the product.
- **AccessBrief** — current 2026 submission inspected as a competitive benchmark for inspectability/safety proof; not treated as a winner.

## B1. Product appears immediately
Winner pattern: Art Museum and Voice Blast enter the real product in roughly the first 0–3 seconds.

Hard Ripple benchmark:
- [ ] Ripple/product interaction begins at **0:00–0:03**.
- [ ] No generic logo reel, company intro, founder intro, stock-film intro, or AI-cinematic preamble delays the product.
- [ ] Any contextual/cinematic shot before product is at most a brief transition and cannot obscure what the product is.

## B2. Five-second comprehension gate
At **5 seconds**, a cold viewer must be able to answer at least:
- [ ] What changed / what problem just occurred?
- [ ] What product is responding?

If an independent reviewer cannot answer both, FAIL.

## B3. Ten-second differentiation gate
At **10 seconds**, a cold viewer must understand:
- [ ] One change has downstream consequences.
- [ ] Ripple is reasoning about the cascade rather than merely acknowledging the message.

If the opening could still be mistaken for a generic chatbot or travel assistant, FAIL.

## B4. Twenty-second value/proof gate
By **20 seconds** the viewer must have seen enough real/verified evidence to understand:
- [ ] concrete downstream impact;
- [ ] concrete repair/value;
- [ ] that Ripple does not silently execute unapproved changes;
- [ ] that execution produces inspectable outcomes.

Exact timing can vary by a few seconds, but all four ideas must be established in the opening proof-trailer.

## B5. The product is the spectacle
Winner pattern: the winning demos rely on interaction/result rhythm more than decorative cinema.

- [ ] The most impressive visual moment represents a real Ripple state, computation, result, or verified consequence.
- [ ] Motion graphics explain actual product behavior; they do not replace missing behavior.
- [ ] At least half of the useful runtime is direct product interaction or direct evidence derived from it.
- [ ] A viewer never has to wait through a visual flourish to discover whether the product works.

## B6. One memorable mechanism
Winner pattern: Art Museum repeatedly demonstrates request -> contextual result; Voice Blast repeatedly demonstrates hear -> answer -> score.

Ripple benchmark:
- [ ] One mechanism dominates the film: **change -> cascade -> repair -> approval -> execution -> proof**.
- [ ] Supporting technologies serve that mechanism rather than competing for attention.
- [ ] No feature tour.
- [ ] No unrelated capability is included solely because it exists.

## B7. Demonstration continuity
Winner pattern: Voice Blast demonstrates a complete game; Art Museum repeatedly shows complete command/result cycles.

- [ ] The golden Ripple scenario is shown as a coherent end-to-end story.
- [ ] The edit may compress latency/waiting, but it may not fabricate intermediate product states.
- [ ] The viewer can reconstruct the causal sequence from the edit.
- [ ] We do not cut away from the product at the exact moment proof is needed.

## B8. Proof density
- [ ] Every major 10–15 second segment adds either a new verified state, a new consequence, a new user decision, or a new proof.
- [ ] No 10-second interval in the body exists only to repeat narration already obvious from the screen.
- [ ] Architecture appears only after the product has earned attention.
- [ ] Setup instructions, dependency lists, implementation history, and generic team biography are excluded from the main film.

## B9. Trust is demonstrated, not announced
Competitive lesson from AccessBrief and Ripple's own safety model:
- [ ] Exact approval is visibly bound to a specific plan.
- [ ] Zero-write-before-approval is demonstrated or represented only if verifiably supported by the frozen evidence.
- [ ] Execution produces receipts/auditability.
- [ ] Replay/idempotence is shown only if the frozen build proves it.
- [ ] Safety language does not consume the opening before the value proposition; narrative order remains **CASCADE -> MONEY -> REPAIR -> EXECUTION -> TRUST**.

## B10. Economic consequence is a visual differentiator
- [ ] Verified value numbers are treated as primary story information, not tiny UI metadata.
- [ ] Risk, repair cost, and preserved value are visually distinguishable.
- [ ] Numbers shown in motion graphics are sourced from the exact frozen scenario.
- [ ] No round-number embellishment or invented ROI claim.

## B11. Audio is part of product communication
Winner pattern: Voice Blast's feedback sounds and Art Museum's audio environment materially support comprehension/experience.

- [ ] Ripple has a consistent sound grammar for change/cascade, risk, approval, execution, receipt, replay/resolve.
- [ ] Sounds distinguish state changes without becoming arcade-like noise.
- [ ] Narration does not duplicate obvious on-screen text sentence-for-sentence.
- [ ] Voice/dialogue is intelligible on phone speakers.
- [ ] Background music, if any, never competes with product audio or speech.
- [ ] The video still communicates core state changes if music is muted.

## B12. Visual coherence / premium finish
- [ ] One consistent typography system.
- [ ] One consistent motion language based on the ripple/cascade metaphor.
- [ ] Stable framing and deliberate zoom/crop; no accidental browser chrome or cursor wandering unless interaction requires it.
- [ ] No unreadable terminal dumps.
- [ ] No low-resolution generated footage in a way that makes the submission look cheaper than the real UI.
- [ ] No stock-template aesthetic unrelated to Ripple.
- [ ] Cuts, easing, text timing, and audio hits are intentional and frame-consistent.

## B13. Readability under judge conditions
- [ ] All essential text survives playback at 720p and on a ~6-inch phone display.
- [ ] Key numbers are readable without pausing.
- [ ] No essential label appears for less than the time needed to read it.
- [ ] Captions/subtitles do not cover product evidence.

## B14. Claim-to-evidence integrity
- [ ] Every technical/platform claim in narration or on-screen copy has a corresponding frozen evidence item.
- [ ] `VERIFIED`, `SIMULATED`, and `NOT SHOWN/NOT CLAIMED` boundaries are respected.
- [ ] AWS, Alexa+, Local Inspector, external-provider, latency, and deployment claims are included only at the capability state proven at VIDEO FREEZE.
- [ ] No future-state language is edited to sound like present-state proof.

## B15. Generality without feature-bloat
- [ ] Golden travel scenario remains the main proof.
- [ ] A second scenario is included only if it establishes generality materially faster than narration could.
- [ ] If retained, second scenario target is **<= 10–12 seconds**.
- [ ] Second scenario may not introduce a new interaction model that dilutes the core mechanism.

## B16. Ending recall
- [ ] Ending restates the core product idea, not the technology stack.
- [ ] Locked pitch is used unless a later evidence-backed change is explicitly approved: **"Tell Alexa one thing that changed. Ripple fixes what breaks downstream."**
- [ ] Final frame is clean and readable long enough to register.
- [ ] No long credits sequence consumes judge attention; legal/asset attribution goes in description or a minimal final card where required.

---

# LAYER 3 — RIPPLE-SPECIFIC PROOF-TRAILER GATE

This is the current target opening. Values remain provisional until VIDEO FREEZE.

Target sequence:
- 0:00–0:03 — real Ripple input: flight cancelled / arrival tomorrow 18:00
- 0:03–0:07 — dependency cascade: five downstream impacts
- 0:07–0:11 — verified economic exposure
- 0:11–0:15 — verified repair cost / value preserved
- 0:15–0:18 — exact approval
- 0:18–0:21 — bounded execution / receipts / notifications
- 0:21–0:23 — replay / deduplication proof
- 0:23–0:26 — Ripple mark + locked pitch

Mandatory opening acceptance:
- [ ] At 5s: problem + product understood.
- [ ] At 10s: cascade/differentiator understood.
- [ ] By ~20–23s: value + approval + execution proof understood.
- [ ] Opening contains real product footage/evidence from the frozen build.
- [ ] No shot exists only to make the intro look expensive.

If this opening fails independent cold-viewer review, the rest of the video may not be declared GOOD even if technically polished.

---

# LAYER 4 — MASTER TECHNICAL QUALITY GATE

- [ ] 1920x1080 master.
- [ ] 16:9.
- [ ] H.264 video.
- [ ] AAC audio.
- [ ] Duration < 180 seconds.
- [ ] No unintended black frames, frozen frames, missing audio, clipping, dropped overlays, or corrupted transitions.
- [ ] Speech loudness is consistent; no audible digital clipping.
- [ ] Captions/subtitles are temporally aligned where used.
- [ ] Export has been watched end-to-end after final encode, not only inspected on the timeline.
- [ ] `video/validate_master.py` passes automated checks.

---

# LAYER 5 — ADVERSARIAL HUMAN REVIEW

A final master must pass at least these independent review questions. Reviewers should not be briefed on Ripple beforehand.

## Cold-view test
By 5s reviewer can state:
- [ ] what changed;
- [ ] that Ripple is responding.

By 10s reviewer can state:
- [ ] that one change causes several downstream problems;
- [ ] that Ripple reasons across those dependencies.

By 20–25s reviewer can state:
- [ ] why the solution has concrete value;
- [ ] that the user approves before execution;
- [ ] that execution is auditable/proven.

After the full film reviewer can state, without prompting:
- [ ] the one-sentence Ripple idea;
- [ ] one specific customer benefit;
- [ ] one specific technical/trust property;
- [ ] why this is more than a normal assistant/chatbot;
- [ ] whether they believe the demo is real and why.

## Skeptic test
Reviewer is explicitly asked to find:
- [ ] any moment that looks simulated but is presented as real;
- [ ] any unsupported claim;
- [ ] any confusing causal jump;
- [ ] any unreadable text;
- [ ] any slow/filler section;
- [ ] any feature that distracts from the central mechanism;
- [ ] any place where polish appears to hide lack of proof.

Any credible finding is a FAIL until fixed or explicitly disproven with evidence.

---

# STATUS RULES

## PREPRODUCTION
Structure/tooling may be prepared. No claim that the film itself is GOOD/READY.

## VIDEO-READY CANDIDATE
Exact source SHA, deployment, scenario values, interaction flow, platform claims, and evidence are frozen.

## ROUGH CUT
Can be reviewed for timing/comprehension. Not GOOD/READY.

## GOOD
May be used only when:
- Layer 0: all applicable PASS;
- Layer 1: all PASS;
- Layer 2: all applicable PASS;
- Layer 3: all PASS;
- no unresolved evidence-integrity issue.

## READY / SUBMISSION-READY
May be used only when:
- all GOOD conditions pass;
- Layer 4 all PASS;
- Layer 5 all PASS;
- final encoded master itself was audited, not only the project/timeline;
- public hosting/link validation passes;
- asset/license manifest is complete.

**There is no score-based override. A 95/100-looking video with one failed mandatory criterion is NOT READY.**

---

# OPTIONAL SCORE — FOR COMPARISON, NOT FOR OVERRIDING FAILURES

After all mandatory gates pass, score 0–5 in each category for optimization:

1. Immediate comprehension
2. Differentiation / idea memorability
3. Real-product credibility
4. Technical proof density
5. Interaction/design clarity
6. Customer/economic impact
7. Trust/safety proof
8. Visual polish
9. Audio polish
10. Pacing / absence of filler

Maximum: 50.

Interpretation:
- 45–50: winner-caliber target range
- 40–44: strong, but still search for concrete weaknesses
- 35–39: acceptable submission quality, not target quality
- <35: rebuild weakest sections

Again: the score is secondary. **All mandatory gates must pass first.**

---

# CHANGE DISCIPLINE

This standard is LOCKED after adoption.

It may change only when:
1. Amazon changes official rules/criteria;
2. new credible winner/competitor evidence adds or invalidates a benchmark;
3. a benchmark is proven inappropriate for Ripple;
4. the user explicitly approves a change.

Changes must be delta-based and logged. Do not weaken a criterion merely because the current cut fails it.
