# Ripple — Canonical WOW Film Storyboard

**Status:** LOCKED for Gate 4 production  
**Master:** 1920×1080, 30 fps, 16:9  
**Target runtime:** 2:15 (4050 frames)  
**Truth source:** `scripts/canonical_demo_trace.py` output conforming to `docs/CANONICAL_DEMO_TRACE.schema.json`  
**Product thesis:** **The conversation is temporary. The promise is not.**

This replaces the old flight-cascade/$116→$42→$74 video as the canonical Continuous Promise Preservation film. The old video material is historical only.

## Production rules

1. Product-state claims come from `canonical_demo_trace`; do not type state/version/write/receipt numbers by hand into animation code.
2. `meaning confirmation` and `exact action approval` are visibly separate authority gates.
3. Never imply a real Alexa+ production-client session. Label the experience **Simulated Alexa+ host · real Ripple MCP behavior** where needed.
4. Household world/provider is a deterministic digital twin. Never imply physical smart-home writes.
5. No generative model may create UI text, contract content, approval content, version numbers, receipts, or proof claims.
6. No terminal scrolling as primary visual evidence.
7. No more than three simultaneous concepts on screen. The film must read on a laptop at normal YouTube size.
8. The invariant rail is spatially stable: repairs move around it; the protected invariant never moves. This is the signature visual metaphor.
9. Motion is semantic, not decorative: amber = changed assumption/world fact; red = threatened invariant; blue/violet = Ripple computation/repair; green = independently verified effect.
10. Final master must stay under 2:25 even after captions; nominal cut is 2:15.

## Canonical visual objects

- **Promise Contract** — the confirmed human meaning, represented as a clean card with goal, invariant rail, assumptions and authority.
- **Invariant Rail** — fixed horizontal/vertical spine; protected truth that must remain true.
- **World State** — compact live-fact card, versioned.
- **Plan Path** — the current bounded action path.
- **Threat Fracture** — red discontinuity where the current plan would violate the contract after world change.
- **Minimal Repair** — only the necessary plan segment morphs; unchanged segments retain position.
- **Authority Gates** — two physically separate gates: `MEANING CONFIRMED` and `ACTION APPROVED`.
- **Receipt** — verified effect card with read-back check.
- **Session Shell** — transient Alexa/MCP conversation container around a durable promise core.

## Frame-locked storyboard

| Frames | Time | Beat | Visual / motion | Voiceover / on-screen copy | Trace binding / acceptance |
|---:|---:|---|---|---|---|
| 0000–0149 | 0:00–0:05 | Cold open | Near-black ivory field. A thin luminous line appears. One word resolves: **PROMISE**. | VO: “You gave an agent a promise.” | No product-state claim. Brand-only. |
| 0150–0299 | 0:05–0:10 | Reality changes | A second line labeled **REALITY** crosses the first and shifts laterally. The plan path begins to shear. | VO: “Then reality changed.” | No state numbers yet. |
| 0300–0539 | 0:10–0:18 | Human intent | Simulated Alexa+ shell appears around the real hero utterance. Text condenses into a Promise Contract. | Screen: “Make sure the house is ready — but Mom is staying here tonight.” Small label: **Simulated Alexa+ host**. VO: “Ripple does not preserve a chat turn. It preserves what the human meant.” | `draft` → `meaning_confirmed`; contract version must come from trace. |
| 0540–0839 | 0:18–0:28 | Contract anatomy | Camera pushes into four contract layers: GOAL / INVARIANTS / ASSUMPTIONS / AUTHORITY. Invariant rail locks into place. | VO: “Meaning becomes a versioned contract: what may change, and what must remain true.” | Contract data derives from hero fixture. No invented fields. |
| 0840–1139 | 0:28–0:38 | Initial safe plan | World v1 card docks left. Plan path forms around fixed invariant rail. A tiny approval gate is visible but not yet the focus. | Screen: **SAFE PLAN · bounded · versioned**. | `initial_plan`; show actual `world_version`, `plan_version`, decision. |
| 1140–1439 | 0:38–0:48 | WOW #1 — world event | `guest_present: true → false` flips in amber. The old plan continues for ~8 frames, then a red fracture propagates toward invariant rail. Rail itself does not move. | VO: “Mom goes out. The old assumption is false — but her access is still protected.” | `mom_leaves`; `guest_stays=false`; `guest_access=true`. |
| 1440–1769 | 0:48–0:59 | Threat becomes visible | Freeze just before collision. Red text: **CURRENT PLAN WOULD BREAK THE PROMISE**. Threat violations materialize beside the fracture. | VO: “Ripple projects the plan forward before the promise is broken.” | `threat` / violations from trace. Never fabricate violation IDs. |
| 1770–2189 | 0:59–1:13 | WOW #2 — minimal repair | Everything desaturates except invariant rail and broken plan segment. Ripple computation pulses once. Only the affected segment detaches, bends around the constraint, and reconnects. Unchanged plan geometry remains pixel-stable. | Screen sequentially: **1 WORLD CHANGE** → **MINIMAL REPAIR** → **0 PROTECTED ACCESS CHANGES**. VO: “It repairs the smallest safe delta. The protected invariant never moves.” | `repair_after_mom_leaves`; plan/binding from trace. “0 protected access changes” is valid only if no action writes `guest_access`. |
| 2190–2459 | 1:13–1:22 | Second world change | Departure time slides from old to new target. Existing path again becomes threatened; a new bounded segment is proposed. | VO: “Then the departure moves. Ripple repairs again — without rewriting the promise.” | `departure_delayed`; same `contract_version`; threat includes actual violation set. |
| 2460–2729 | 1:22–1:31 | Two authority gates | Contract passes through **MEANING CONFIRMED** gate. Camera pans to a distinct **ACTION APPROVAL** gate that remains closed. Provider-write counter stays at current trace value. | Screen: **Meaning confirmed ≠ Action approved**. VO: “Understanding the promise is not permission to act.” | Meaning confirmation and action approval must be distinct trace events. |
| 2730–2969 | 1:31–1:39 | Exact approval | Binding card expands: contract/world/plan versions + exact action delta. Human approval closes only over that binding. | VO: “Approval is bound to this exact version of the world and this exact repair.” | `exact_approval`; values from binding in trace. |
| 2970–3239 | 1:39–1:48 | Evidence before action | At the scheduled time, path reaches an evidence gate and stops. `family_departed=false` remains visible. No green receipt appears. | Screen: **WAIT FOR EVIDENCE**. VO: “A timetable is not proof that the family actually left.” | `wait_for_departure_evidence`; `decision=WAIT_FOR_EVIDENCE`; no new write. |
| 3240–3449 | 1:48–1:55 | Execute + verify | Trusted world event flips `family_departed=true`. Gate opens, exact delta executes. Receipt travels out, then a separate read-back returns green. | Screen: **EXECUTE → READ BACK → VERIFIED**. | `verified_execution`; at least one verified receipt; write count from trace. |
| 3450–3719 | 1:55–2:04 | WOW #3 — session death | Entire Alexa/MCP Session Shell shatters/fades to black while the Promise Contract core remains. Big copy: **SESSION ENDED**. After 12-frame silence: **NEW SESSION**. New shell forms around the same promise core. | VO: “The conversation ends.” Beat. “The promise doesn’t.” | `session_reconstructed`; same contract id/version, persisted state, same verified receipt count. |
| 3720–3869 | 2:04–2:09 | Replay safety | Execute pulse is sent again. It reaches receipt ledger and dissolves. Write counter does not move. | Screen: **REPLAY → 0 DUPLICATE EFFECTS**. | `replay_deduplicated`; write count before = after. |
| 3870–3989 | 2:09–2:13 | Real stack proof | Four clean proof nodes appear, not logos-first: **Bedrock normalization · DynamoDB durability · CloudWatch evidence · MCP 2025-11-25**. Small footnote separates live AWS proof from simulated household provider. | VO: “The model interprets. Deterministic policy protects. Durable state and receipts prove what happened.” | Claims must remain supported by exact-SHA live evidence docs; household execution remains labelled digital twin. |
| 3990–4049 | 2:13–2:15 | Memory anchor | Everything collapses to Ripple mark and one line. | **Tell Ripple what must remain true.** / **Ripple keeps the promise as the world changes.** | Brand statement; no new factual claim. |

## Audio map

- 0:05 world-change: low transient, no cinematic boom.
- 0:38 assumption flip: dry amber tick + low sub pulse.
- 0:48 threat fracture: restrained tension texture, never alarm-like.
- 0:59 repair: one clean rising mechanical gesture; no “AI sparkle.”
- 1:22 meaning gate: soft confirmation tick.
- 1:31 action approval: distinct heavier click.
- 1:39 wait-for-evidence: music thins; no success sound.
- 1:48 verified read-back: two-stage sound — execution then verification.
- 1:55 session-ended: near-silence for ~0.4 s.
- 2:04 replay dedupe: dry suppressed click.
- 2:13 outro: short original Ripple sting.

## Camera / motion language

- 80% orthographic/product-motion feel; no gratuitous parallax.
- Use perspective only for Promise Contract depth and Session Shell transition.
- Easing: predominantly custom cubic / critically damped; no bounce except tiny physical confirmation feedback.
- Cuts should follow semantic state changes, not music beats.
- No shot > 12 s without a meaningful state transition.

## Claim boundary labels

The final video may say:

- real Bedrock normalization was live-proven on exact SHA evidence;
- durable DynamoDB state/receipts/replay were live-proven;
- CloudWatch read-back evidence was live-proven;
- MCP 2025-11-25 compatibility is tested;
- simulated Alexa+ host exercises real Ripple MCP behavior;
- household provider shown in the hero film is a digital twin;
- meaning confirmation and action approval are separate authority events;
- session replacement does not define promise persistence.

The final video must not say or imply:

- a production Alexa+ client session was exercised;
- physical smart-home devices were controlled;
- Amazon endorsed Ripple;
- the digital-twin household receipts are physical-provider receipts.

## Gate 4 acceptance

Gate 4 is PASS only when all are true:

- master duration < 2:25 and nominal narrative <= 2:15;
- every product-state number/copy is generated from the canonical trace or separately cited live evidence;
- all three WOW moments survive muted playback and are understandable without narration;
- at 50% display scale, all required text remains legible;
- meaning confirmation and action approval cannot be mistaken for the same event;
- session-reconstruction shot uses the same persisted promise identity and verified state;
- no claim exceeds its evidence class;
- final anti-hallucination/drift audit reports no stale old-product storyline.
