# Ripple — Canonical WOW Film Storyboard

**Status:** VISUAL LOCK v4 — audio production in progress  
**Master target:** 1920×1080, 30 fps, 16:9  
**Runtime:** 2:15 / 4050 frames  
**Truth source:** `scripts/canonical_demo_trace.py` output conforming to `docs/CANONICAL_DEMO_TRACE.schema.json`  
**Product thesis:** **The conversation is temporary. The promise is not.**

This supersedes the old flight-cascade/$116→$42→$74 film. The canonical story is Continuous Promise Preservation.

## Production rules

1. Product-state numbers, versions, write counts and receipt counts come from `canonical_demo_trace`; they are not typed manually into production motion code.
2. `meaning confirmation` and `exact action approval` are separate visible authority gates.
3. Never imply a real Alexa+ production-client session. The hackathon experience is a simulated Alexa+ host exercising real Ripple MCP behavior.
4. The household provider is a deterministic digital twin. Never imply physical smart-home writes.
5. No generative model creates UI text, contract content, approval content, versions, receipts or technical proof claims.
6. The protected invariant rail remains spatially stable. Red is used only for explicit invariant violations reported by the trace.
7. Semantic color grammar: amber = changed world/assumption or stale plan; red = explicit invariant threat; violet = Ripple contract/repair/authority; green = independently verified effect.
8. Motion follows state changes, not decorative beats.
9. Live AWS evidence, current exact-SHA CI evidence and digital-twin hero evidence remain visibly distinct evidence classes.
10. Final release claims require a final claim-vs-evidence audit; any live-service claim that depends on release SHA must be rerun on the frozen candidate SHA.

## Frame-locked visual lock v4

| Frames | Time | Beat | Visual / motion | Canonical truth binding |
|---:|---:|---|---|---|
| 0000–0449 | 0:00–0:15 | Promise → reality → human intent | `PROMISE` resolves; reality shears the plan; simulated Alexa+ shell reveals the exact hero utterance and condenses it into a Promise Contract. | Brand-only opening, then `draft` / `meaning_confirmed`; hero utterance from `src/ripple/promises/examples.py`. |
| 0450–0989 | 0:15–0:33 | Contract anatomy + first plan | GOAL / INVARIANTS / ASSUMPTIONS / AUTHORITY become visible. Four fixture invariants lock in. World v1 and Plan v1 dock below. | `meaning_confirmed` + `initial_plan`; show trace-derived contract/world/plan versions, `REQUEST_APPROVAL`, `writes=0`, and first bound action. |
| 0990–1439 | 0:33–0:48 | WOW #1 — Mom leaves / minimal repair | `guest_present` and `guest_stays` flip false in amber. `guest_access=true` remains fixed. The stale single departure plan is reprojected into the trace-derived two-action plan. | `mom_leaves` + `repair_after_mom_leaves`; this beat is a goal/plan mismatch, not an access-invariant violation. No action writes `guest_access`. |
| 1440–1769 | 0:48–0:59 | First bounded effect | Exact approval binds contract v1/world v2/plan v2. Only the due `guest_heat→eco` delta executes. Independent read-back returns verified. | `repair_after_mom_leaves_approved` + `due_repair_executed`; world v2→v3, plan v2→v3, receipts 0→1, writes 0→1. |
| 1770–1883 | 0:59–1:02.8 | WOW #2 — explicit invariant threat | Departure moves. Two rails fracture red: `departure_timing` and `occupied_security`. Access remains unthreatened. | `departure_delayed`; world v4 / plan v4 / same contract v1; violation IDs come directly from trace. |
| 1884–2243 | 1:02.8–1:14.8 | Meaning ≠ permission | Two physically separate authority gates: MEANING CONFIRMED and ACTION APPROVAL. Provider-write counter remains unchanged while permission is absent. | Human meaning confirmation and action approval are distinct events and channels. |
| 2244–2543 | 1:14.8–1:24.8 | Stale deadline safety | The clock reaches the old departure time after the world changed. Nothing fires. | `old_departure_no_effect`; old time derives from `initial_plan`, new time from `departure_delayed`; writes remain 1→1, common mode HOME, alarm STAY. |
| 2544–2879 | 1:24.8–1:36 | Evidence gate → verified execution | Exact binding is shown. At the new departure, Ripple waits because `family_departed=false`. Independent evidence changes the world, invalidates the old binding, requires fresh exact approval, then execution and read-back complete. | `exact_approval` → `wait_for_departure_evidence` → `family_departed_evidence` → `final_exact_approval` → `verified_execution`; final shown values world v6 / plan v5 / receipts 2 / writes 2. |
| 2880–3239 | 1:36–1:48 | WOW #3 — session death / reconstruction | Conversation shell dies while Promise Contract remains. A new shell forms around the same persisted promise. | `session_reconstructed`; contract v1 / world v6 / plan v5 / receipts 2 / writes 2; `session_generation=2`. |
| 3240–3389 | 1:48–1:53 | Replay safety | A fresh replay reaches the durable receipt boundary and dissolves. | `replay_deduplicated`; writes 2→2, zero duplicate effects. |
| 3390–4049 | 1:53–2:15 | Completion → proof classes → memory anchor | Independent completion closes the promise as SATISFIED. Then four compact proof nodes distinguish Bedrock, DynamoDB, CloudWatch and MCP evidence. Film collapses to the thesis. | `completion_verified`: contract v1 / world v7 / plan v5 / receipts 2 / writes 2. Hero household = digital twin; Alexa+ host = simulated; AWS service evidence = live gate; MCP = current exact-SHA CI conformance. |

## Locked on-screen memory anchors

- **PROMISE — what must remain true**
- **Meaning confirmed ≠ Action approved**
- **STALE DEADLINE → 0 NEW EFFECTS**
- **WAIT FOR EVIDENCE**
- **EXECUTE → READ BACK → VERIFIED**
- **REPLAY → 0 DUPLICATE EFFECTS**
- **The session is temporary. The promise isn’t.**
- **Tell Ripple what must remain true. Ripple keeps the promise as the world changes.**

## Audio map for the 2:15 lock

- 0:05 reality change: restrained low transient.
- 0:33 Mom leaves: dry amber tick; no alarm cue.
- 0:48 first exact approval: heavier mechanical click.
- 0:55 read-back: distinct verification chime.
- 0:59 explicit threat: low sub pulse + restrained fracture texture.
- 1:02.8 meaning gate: soft confirmation tick.
- 1:07 action approval: separate heavier click.
- 1:18 stale deadline: deliberately suppressed dry cue — no success sound.
- 1:25 evidence gate: score thins.
- ~1:32 execution/read-back: paired execution + verification cue.
- 1:36 session ended: near-silence before reconstruction swell.
- 1:49 replay: dry suppressed click.
- 1:53 SATISFIED: restrained green harmonic cue.
- ~1:59–2:03 proof nodes: four small ticks.
- 2:08 onward: original Ripple outro bloom.

## Current voiceover strategy

Narration is deliberately shorter than the full 135 seconds. Semantic pauses are part of the design. The voice must never narrate every visible field; it explains the idea while trace-bound UI supplies proof.

## Claim boundaries

The film may state now:

- real AWS Bedrock inference was live-proven;
- live DynamoDB durability/CAS/replay evidence was proven;
- live CloudWatch engine evidence/read-back was proven;
- MCP 2025-11-25 conformance is tested on the current quality gate;
- the hackathon-permitted simulated Alexa+ host exercises real Ripple MCP behavior;
- the household hero provider is a deterministic digital twin;
- meaning confirmation and exact action approval are separate authority events;
- promise state survives conversational session replacement;
- replay produces zero duplicate effects in the canonical hero trace.

The final film must not say or imply:

- a production Alexa+ client session was exercised;
- physical smart-home devices were controlled;
- Amazon endorsed Ripple;
- digital-twin receipts are physical-device receipts;
- a release-SHA live claim was rerun unless that exact proof has actually completed.

## Gate 4 acceptance

Gate 4 becomes PASS only when all are true:

- final encoded master is <= 2:15 nominal narrative and < 2:25 absolute limit;
- every product-state number/copy is trace-generated or separately evidenced;
- no hard-coded trace number remains in production motion code;
- all three WOW moments survive muted playback;
- required text remains legible at 50% display scale;
- meaning confirmation and action approval cannot be mistaken for the same event;
- session-reconstruction uses the same persisted promise state;
- audio mix has no clipping and leaves VO headroom;
- final frozen-SHA claim audit is complete;
- final anti-hallucination/drift audit reports no stale old-product storyline.
