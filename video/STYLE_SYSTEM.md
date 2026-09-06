# Ripple video style system

Status: preproduction, independent of final product UI.

The submission video should feel like one coherent product film, not a collage of screen recording, AI clips, slides, and diagrams.

## 1. Visual metaphor

The visual language is the ripple itself:
- one state change emits a wave
- the wave reveals dependent nodes
- affected nodes accumulate exposure
- approval changes the direction from propagation to repair
- repair flows through bounded actions
- receipts remain as proof after motion stops

This metaphor must be used sparingly and consistently. It is not decorative particle animation.

## 2. Product footage treatment

Real Ripple footage is primary evidence.

Rules:
- preserve readable UI
- avoid fake cursor wandering
- remove waiting/dead time, not causal steps
- use punch-in/zoom only to focus on evidence
- never crop away the part of the UI that establishes context
- do not overlay effects that obscure approval, receipts, money, or replay proof
- when a state transition matters, show before and after clearly

## 3. Motion graphics

Preferred primitives:
- concentric wave / expanding front
- node activation
- edge pulse
- cost aggregation
- plan compression
- receipt arrival
- replay wave with intentionally absent write events

Avoid:
- generic glowing AI brain
- random network mesh
- excessive parallax
- HUD decoration unrelated to product state
- stock-code rain
- logo clouds

## 4. Typography

Use a single modern sans-serif family already legally available in the render environment. Do not add licensed fonts to the repository.

Hierarchy:
- proof number / critical claim: very large
- state label: medium
- supporting detail: small but readable at 1080p

On-screen text should be short enough to understand without pausing.

Preferred proof cards:
`5 DOWNSTREAM IMPACTS`
`$116 AT RISK`
`$42 REPAIR`
`$74 PRESERVED`
`5 RECEIPTS`
`0 DUPLICATE WRITES`

All values must be replaced by the VIDEO FREEZE values if the final verified scenario changes.

## 5. Color semantics

Do not hard-code a decorative palette before the final UI is frozen. Derive production colors from Ripple's actual final UI/brand.

Semantic roles must stay stable:
- neutral: unchanged/context
- risk: affected / exposure
- proposed: candidate repair
- approved/executed: bounded successful action
- proof: receipt / verified outcome

Color must not be the only carrier of meaning; use labels, shape/state, or motion as well.

## 6. Camera language

For motion scenes, virtual camera behavior should mimic product cinematography:
- direct push toward the consequence that matters
- one continuous move through a dependency cascade when possible
- hard cuts for proof/approval moments
- no gratuitous orbiting

For product capture:
- default straight-on frame
- controlled punch-ins
- avoid perspective distortion and fake device mockups unless a real device shot materially proves Alexa behavior

## 7. Sound grammar

Sound should make state transitions legible even with minimal narration.

### Change / failure
Low, short impact. No disaster-movie boom.

### Cascade
One propagating sweep plus tightly spaced dependent ticks.

### Economic aggregation
Subtle ticks/count texture; stop cleanly on the verified total.

### Approval
One precise mechanical lock/click.

### Execution
Short, discrete action ticks. Number of audible actions should not imply more writes than actually occur.

### Receipt
Small, clean confirmation chime. Avoid gamified coin sounds.

### Replay
Second ripple/sweep with deliberately missing write ticks, resolving into silence before `0 DUPLICATE WRITES`.

### Brand signature
A 1-2 second sonic motif derived from the ripple sweep. Reuse at final card.

## 8. Narration

Narration is subordinate to visual proof.

Avoid:
- `Ripple is an innovative AI-powered...`
- reading text already visible on screen
- listing technologies
- unsupported superlatives

Prefer short causal statements, for example:
- `One change can break five things downstream.`
- `Ripple prices the exposure before it acts.`
- `Nothing writes until you approve the exact plan.`
- `Replay leaves no duplicate writes.`

Final wording remains editable until VIDEO FREEZE and claim audit.

## 9. Optional contextual footage

Contextual film/AI footage is optional and non-critical.

Use only if it adds information or emotional compression that product footage cannot. Maximum individual shot should normally be 1-3 seconds. It must never delay the first real product state.

Any external asset requires license/source entry in ASSET_MANIFEST.csv.

## 10. Editing rhythm

Opening 0-26s: dense, high information, short shots.
Golden flow: slower, credible, readable.
Architecture: compressed and diagrammatic.
Platform proof: sober evidence.
Ending: simplify, decelerate, leave one memorable sentence.

The edit should feel confident rather than frantic.
