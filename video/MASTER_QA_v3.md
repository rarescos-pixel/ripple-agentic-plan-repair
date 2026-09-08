# Ripple Video v3 — Master QA / Continuation Packet

Status: **MACHINE-QUALIFIED HUMAN-REVIEW CANDIDATE — NOT READY / NOT FINAL / NOT SUBMISSION-READY**

Recorded: 2026-09-08

## Canonical product state

- Frozen product source SHA: `c6766c5919ea903530a8da2d526d64a49b7f0578`
- Public AWS runtime used for evidence: `https://ri-9fd0e66d62464ec4ae642ccf46e6864d.ecs.eu-central-1.on.aws`
- Golden raw capture SHA-256: `c564486eaf86355cd1d10a5ded764353876fc27900d80f9e67c3b5d527540f32`
- Golden raw capture: 1920×1080, 25 fps, 23.28 s
- Golden evidence gate: `7/7 PASS`
- Verified causal checkpoints: changed fact → impacts/economics → exact approval → execution → five receipts → replay/dedup proof

## Current master candidate

Local review filename: `ripple-v3-master-candidate-v3.mp4`

SHA-256:

`1f960ba67b583a5c9865a9592cf657dfcf34a785b577cc503bb08018349a99af`

State: **VERIFIED MACHINE-QUALIFIED / HUMAN REVIEW REQUIRED**

Mechanical properties verified from the final encoded file:

- duration: `138.000 s` (`2:18`)
- resolution: `1920×1080`
- aspect: `16:9`
- video: H.264 High, 25 fps
- audio: AAC-LC, 48 kHz mono
- full video+audio decode: PASS
- canonical `video/validate_master.py` logic: PASS

## Visual proof verification

The final candidate's encoded H.264 elementary stream SHA-256 is:

`dc49af8116ffb1677ec699ef5078c0996161dfcd8cccf89b874dbe6d810a894c`

It is bit-identical to the visually audited candidate stream. Therefore the audited frames transfer exactly to this final candidate.

Verified visible beats include:

1. changed flight fact at frame one;
2. downstream cascade;
3. `$116` at risk;
4. `$42` repair / `$74` preserved;
5. `External writes before approval: 0`;
6. `Approve $42 repair`;
7. customer-approved execution;
8. five authoritative receipts;
9. replay: `5/5` deduplicated and unique writes remain five;
10. trust boundary / fail-closed model;
11. AWS / MCP runtime proof;
12. Event Operations generality proof;
13. U.S. DOT/BTS disruption anchor;
14. adversarial proof;
15. customer outcome;
16. locked Ripple ending pitch.

Caption placement was audited across the opening/product proof and all evidence cards. Essential values, CTA, receipts, replay proof, sources and boundaries remain readable.

## Timing corrections locked

The canonical 138 s timeline follows `VIDEO_SCRIPT_v3.md`.

Two raw-capture alignment defects were corrected without re-executing the demo:

- 20–23 s execution segment uses a precise decode seek from the verified golden raw capture at 9.55 s.
- 23–36 s contiguous approval→execution→receipts segment is aligned from raw at 5.80 s so execution and the receipt narration/caption boundary coincide.

Observed transition audit:

- 26.5 s: exact approval visible;
- 26.9 s: execution / receipts visible;
- 27.2 s: execution / receipts visible with `Five actions produce five authoritative receipts.` caption;
- 40 s: replay proof visible.

## Captions

Final caption source: `captions-v3-v2.ass`

- English
- 28 timed events derived from `VIDEO_SCRIPT_v3.md`
- 1920×1080 safe layout
- opaque dark background for judge-condition readability
- no essential proof is obscured

## Audio / licensing state

The final candidate does **not** contain Microsoft Edge Read Aloud / edge-tts voice output.

That draft narration path is **INVALIDATED FOR FINAL** because redistribution/commercial publication rights were not independently verified.

Final audio uses only project-generated procedural sound grammar plus silence:

- generator: `video/generate_sfx_v3.py`
- source WAV SHA-256: `d87426bd1ae22c96b19aaa04d1f093e8aacc5052dd74fbca5b02aa0fddb81294`
- deterministic reproduction: bit-identical PASS
- 48 kHz mono
- no third-party music or samples

Verified final AAC cue presence after encoding:

- change: ~−27.6 dBFS
- cascade: ~−42.3 dBFS
- risk: ~−31.2 dBFS
- approval: ~−39.3 dBFS
- receipts: ~−45.7 dBFS
- continuous-proof receipts: ~−46.0 dBFS
- replay: ~−34.5 dBFS
- ending: ~−34.6 dBFS

Sound grammar therefore survives final AAC encoding and distinguishes the required product-state transitions without music.

## Asset provenance

`video/ASSET_MANIFEST.csv` is the canonical asset ledger.

Current locked rules:

- frozen Ripple capture: project-owned / used;
- evidence/motion cards: project-generated / used;
- captions: project-generated / used;
- procedural SFX: project-generated / used;
- Edge TTS draft voiceover: excluded / invalidated;
- optional third-party context: not used;
- optional music: not used.

## Invalidated paths

Do not promote or reuse as final:

- earlier caption style with insufficient contrast;
- `ripple-v3-master-candidate-v2.mp4` — technically/visually valid draft but contains Edge Read Aloud voiceover with unverified redistribution rights;
- earlier master candidate before caption contrast correction;
- `rough_visual_v3b.mp4` — useful visual rough, but approval/execution timing did not map tightly enough to the canonical script;
- automated browser rough-cut recorder path that blocked during playback; superseded by deterministic FFmpeg timeline construction.

## Machine gates — current state

- product freeze identity: PASS
- golden raw capture reproducibility/evidence: PASS
- exact approval / zero preapproval writes: PASS
- five receipts: PASS
- replay/dedup proof: PASS
- 1920×1080 / H.264 / AAC / <3:00: PASS
- canonical mechanical validator: PASS
- final full decode: PASS
- final visual stream identity to audited frames: PASS
- caption readability sampled across all sections: PASS
- claim-to-evidence adjacency: PASS on audited beats
- asset provenance / no unverified final TTS or third-party music: PASS
- procedural sound grammar: PASS

## Remaining mandatory blockers

These are intentionally **not** marked PASS by machine inspection.

### H6 / independent delayed memory test — UNKNOWN

An unbriefed reviewer must still recall after approximately 60 seconds:

1. one change causes a downstream cascade;
2. Ripple proposes a repair with concrete value;
3. exact approval occurs before execution;
4. replay creates zero duplicate writes.

### Human end-to-end master watch — UNKNOWN

The final encoded candidate must be watched end-to-end by a human after the final encode, as required by the canonical acceptance standard.

### Adversarial cold / skeptic review — UNKNOWN

An unbriefed reviewer must run the canonical 5 s / 10 s / 20–25 s comprehension and post-film skeptic questions.

### Public delivery — UNKNOWN

No YouTube/Vimeo public upload has been authorized or verified yet. Final public URL must work unauthenticated before submission readiness can be claimed.

## Locked next action

Do not modify the product or reopen general video development.

Next state change is **independent human review of the exact candidate hash above**. If that review passes, then:

1. promote the exact reviewed bytes to MASTER without re-encoding;
2. upload publicly to YouTube or Vimeo;
3. verify the link from an unauthenticated context;
4. update this packet / final delivery ledger with the reviewed master SHA and public URL.

If human review finds a concrete defect, change only that demonstrated defect and invalidate the reviewed hash; do not restart general video ideation.
