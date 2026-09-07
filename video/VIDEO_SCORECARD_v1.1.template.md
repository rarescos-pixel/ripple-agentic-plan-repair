# Ripple Video Acceptance Scorecard v1.1

Cut / artifact: ____________________
Frozen product SHA: ____________________
Video pipeline SHA: ____________________
Deployment identity / URL: ____________________
Reviewer: ____________________
Review date/time (timezone): ____________________

Use only: `PASS`, `FAIL`, `UNKNOWN`, `N/A-EXPLAINED`.

**Hard rule:** any mandatory FAIL or UNKNOWN means the cut is NOT GOOD / NOT READY, regardless of numeric score.

This scorecard inherits every mandatory criterion from `VIDEO_SCORECARD.template.md` and adds the v1.1 hard gates below. The inherited scorecard must still be completed.

## v1.1 additive hard gates

| ID | Criterion | State | Evidence / timestamp / note |
|---|---|---|---|
| H1 | No >~1.5s dead-air without justified readability hold | UNKNOWN | |
| H2 | >=~70% useful runtime real product / frozen-build evidence | UNKNOWN | |
| H3 | Contiguous change -> cascade -> proposal -> approval -> execution -> receipts proof | UNKNOWN | |
| H4 | Important claims have same-beat or adjacent evidence | UNKNOWN | |
| H5 | Key claims/numbers readable at 720p and ~6-inch phone playback | UNKNOWN | |
| H6 | 60s delayed memory: cascade + value + exact approval + zero duplicate writes | UNKNOWN | |

## Opening timing audit

| Gate | Target | State | Evidence |
|---|---:|---|---|
| Real product visible | 0:00–0:03 | UNKNOWN | |
| Problem + product understood | <=0:05 | UNKNOWN | |
| Cascade / differentiator understood | <=0:10 | UNKNOWN | |
| Verified economics understood | <=0:15 | UNKNOWN | |
| Approval + execution proof established | ~0:20–0:23 | UNKNOWN | |
| Receipts clearly readable | ~0:23–0:30 | UNKNOWN | |
| Replay safety becomes an early primary memory anchor | before deep architecture | UNKNOWN | |

## Real-product dominance audit

Total final runtime: __________
Direct real Ripple product runtime: __________
Direct frozen-build evidence runtime: __________
Decorative/title/architecture-only runtime: __________
Useful runtime product/evidence share: __________ %

State: `UNKNOWN`

## Claim-to-evidence adjacency audit

List every important technical/platform claim and its adjacent proof.

| Claim | Timestamp | Evidence | Adjacent? | State |
|---|---:|---|---|---|
| Alexa+ / simulated surface boundary | | | | UNKNOWN |
| MCP 2025-11-25 Streamable HTTP | | | | UNKNOWN |
| AWS canonical runtime | | | | UNKNOWN |
| Bedrock normalization | | | | UNKNOWN |
| DynamoDB durable approval/receipts/replay | | | | UNKNOWN |
| CloudWatch redacted evidence | | | | UNKNOWN |
| Zero writes before approval | | | | UNKNOWN |
| Five receipts after execution | | | | UNKNOWN |
| Replay 5->5 / zero new provider writes | | | | UNKNOWN |

## Replay memory-anchor audit

Expected simple message:

> Run it again. Nothing happens twice.

Expected verified proof:

- `5/5 DEDUPLICATED`
- `AUTHORITATIVE WRITES: 5 -> 5`
- `NEW PROVIDER WRITES: 0`

State: `UNKNOWN`
Timestamp: __________
Reviewer paraphrase: ________________________________________________

## 60-second delayed memory test

Reviewer must not be prompted with terminology.

| Memory item | State | Exact reviewer recall |
|---|---|---|
| One change causes downstream cascade | UNKNOWN | |
| Ripple proposes repair with concrete value | UNKNOWN | |
| User gives exact approval before execution | UNKNOWN | |
| Replay produces zero duplicate writes | UNKNOWN | |

## Optional optimization score — only after all mandatory gates pass

Score 0–5:

| Category | Score |
|---|---:|
| Immediate comprehension | |
| Differentiation / memorability | |
| Real-product credibility | |
| Technical proof density | |
| Interaction/design clarity | |
| Customer/economic impact | |
| Trust/safety proof | |
| Visual polish | |
| Audio polish | |
| Pacing / no filler | |
| **TOTAL / 50** | |

Interpretation only after all hard gates PASS:

- 48–50 = winner-caliber target
- 46–47 = strong, revise
- <=45 = not final competitive quality

## Final status

- [ ] PREPRODUCTION
- [ ] VIDEO-READY CANDIDATE
- [ ] ROUGH CUT
- [ ] GOOD — all inherited + v1.1 opening/product gates PASS
- [ ] READY / SUBMISSION-READY — all inherited Layers 0–5 + v1.1 hard gates + hosting/licenses PASS

Unresolved blockers:

1. ____________________
2. ____________________
3. ____________________

Exact NEXT state-changing action: ____________________
