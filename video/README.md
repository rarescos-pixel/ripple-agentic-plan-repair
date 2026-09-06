# Ripple Video Production

Status: PREPRODUCTION ONLY until a VIDEO-READY CANDIDATE is declared.

This directory contains submission-video work that is deliberately isolated from production code. It must not change Ripple runtime behavior.

## Canonical quality authority

`video/VIDEO_ACCEPTANCE_STANDARD.md` is the **LOCKED authority** for deciding whether any cut may be called GOOD, READY, FINAL, or SUBMISSION-READY.

Organizer requirements are Layer 0 and must pass first. Winner/competitor-derived benchmarks are an additional stricter layer. **There is no score-based override: one failed mandatory criterion means NOT READY.**

Every real review uses a copy of `video/VIDEO_SCORECARD.template.md` and records evidence/timestamps rather than impressions.

## Goal

Produce a <= 3 minute English demo video that makes the product understandable immediately and proves the strongest claims with real product footage.

Target master: 1920x1080, 16:9, H.264 video + AAC audio, target duration 2:15-2:25.

## Core rule

Do not film the final product before a VIDEO-READY CANDIDATE exists.

Real product footage must come from one exact source revision and one exact deployed build. Motion graphics may visualize verified runtime outputs but may not invent behavior, integrations, money values, platform status, or evidence.

## Narrative order

CASCADE -> MONEY -> REPAIR -> EXECUTION -> TRUST

The first ~25 seconds are a proof-trailer built from the real golden flow, not a cinematic preamble.

## Production phases

1. PREPRODUCTION (safe now)
   - shot list
   - visual language
   - sound grammar
   - capture contract
   - evidence/claim rules
   - asset/license manifest
   - render/output quality gates

2. VIDEO FREEZE
   - exact git SHA
   - exact live URL/deployment identity
   - exact golden scenario values
   - exact interaction steps
   - verified platform claims
   - known exclusions / claims that must not appear

3. CAPTURE
   - deterministic Playwright capture of real Ripple flow
   - preserve unedited source captures
   - no hidden state changes that cannot be reproduced

4. POST
   - motion graphics driven by verified values
   - sound design
   - narration only where visuals are insufficient
   - compositing and pacing

5. ADVERSARIAL AUDIT
   - apply every mandatory gate in `VIDEO_ACCEPTANCE_STANDARD.md`
   - use `VIDEO_SCORECARD.template.md` with PASS/FAIL/UNKNOWN evidence
   - a judge understands Ripple by 5s / 10s / 20s
   - every technical claim maps to evidence
   - no simulated element is presented as independently verified
   - no filler, feature tour, or infrastructure-bloat

## Technology

Backbone, zero required software spend:
- Playwright/Chromium for deterministic real-product capture
- SVG/HTML/Canvas/Three.js or Motion Canvas for data-driven motion graphics
- FFmpeg/ffprobe for edit, compositing, captions, audio mix, encoding, validation
- Python-generated SFX where useful
- GitHub Actions only when it materially reduces manual work and remains free for this public repository

Optional AI/stock footage is non-critical and may only be used for short contextual shots when licensing and cost are verified. The film must remain producible if all optional generators disappear.

## Locked opening concept

0:00-0:03  real Ripple input: flight cancelled / arrival tomorrow 18:00
0:03-0:07  dependency cascade: 5 downstream impacts
0:07-0:11  $116 AT RISK
0:11-0:15  $42 REPAIR -> $74 PRESERVED
0:15-0:18  exact approval
0:18-0:21  bounded execution -> 5 receipts / 3 people notified
0:21-0:23  replay -> 0 duplicate writes
0:23-0:26  RIPPLE + locked pitch

Numbers and labels remain subject to VIDEO FREEZE verification before capture.

## Hard exclusions

- no 15-20 second generic AI-cinematic intro before the product
- no slideshow disguised as video
- no unverified AWS/Alexa+/Inspector claim
- no tech-logo wall
- no feature tour
- no new product feature added only to make the video look better
- no production/main changes from this branch unless separately reviewed and requested
