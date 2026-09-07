# Ripple — Winner Cut Video Script v2

**Target runtime:** 2:35–2:42

**Submission constraints:** public YouTube/Vimeo, English, under 3:00. The first customer value must land before the judge has time to wonder about architecture.

## Core video principle

This is not a screen recording of a hackathon project. It is a product demo with technical proof.

The video must make one idea unforgettable:

> **One change. Five consequences. One safe repair. One exact approval. Five receipts. Zero duplicate writes.**

Do not lead with AWS, MCP, OAuth, GitHub, hashes, diagrams or test matrices. The judge must understand the customer value before any infrastructure appears.

---

## 0:00–0:07 — Hook

Full-screen typography over a clean Ripple background:

> **ONE CANCELLATION.**
> **FIVE BROKEN COMMITMENTS.**

Small Ripple mark only. No architecture logos.

Voiceover:

> “Plans rarely break one thing.”

---

## 0:07–0:19 — Customer → Alexa+

Show the real rules-permitted simulated Alexa+ experience backed by the public MCP server.

Customer says:

> “Our flight home was cancelled. We’ll land tomorrow at six.”

On-screen label, small but unambiguous:

> **Simulated Alexa+ experience · real public Ripple MCP backend**

Voiceover:

> “Ripple starts with one changed fact.”

Do not apologize for the simulation path and do not imply an official Alexa+ production-client session.

---

## 0:19–0:34 — Moment of magic

The Repair Card becomes the dominant visual.

Animate the four numbers one by one, large enough to read instantly:

> **5 commitments affected**
> **$116 at risk**
> **$42 repair cost**
> **$74 preserved**

Then reveal:

> **Approve $42 repair?**

Voiceover:

> “Ripple finds what breaks downstream, prices the consequence set, and proposes one safe repair. Five commitments are affected. One hundred sixteen dollars are at risk. Ripple can repair the cascade for forty-two and preserve seventy-four.”

This is the primary product moment. Hold the numbers long enough to register.

---

## 0:34–0:50 — What actually broke + trust before action

Show the five human-readable commitments, not internal IDs:

- ride
- dinner reservation
- grocery delivery
- pet-care window
- tomorrow’s meeting

At the bottom, show a single proof line:

> **Provider writes before approval: 0**

Voiceover:

> “Instead of making the customer discover five failures across five apps, Ripple exposes the whole cascade before anything is changed.”

Avoid snapshots/hashes in the main visual.

---

## 0:50–1:08 — Exact approval → execution → receipts

Show the exact approval action:

> **Approve $42 repair**

Then animate five receipts arriving, one by one, with clear statuses.

Voiceover:

> “The approval is bound to this exact cost and scope. After approval, Ripple executes only the disclosed actions and returns authoritative receipts.”

On screen briefly:

> **5 actions · 5 receipts**

Do not show terminal output.

---

## 1:08–1:23 — Technical wow: replay safety

Run the exact plan again or reconnect through a fresh session.

Use very large proof text:

> **5/5 DEDUPLICATED**
> **AUTHORITATIVE WRITES: 5 → 5**
> **NEW PROVIDER WRITES: 0**

Voiceover:

> “Run it again. Nothing happens twice. Durable receipts and idempotency suppress duplicate external writes, even after a fresh session.”

This is the most important technical moment in the video. It demonstrates sophisticated safety without requiring the judge to understand implementation details.

---

## 1:23–1:39 — Trust model in one animation

Use a single horizontal animation with five steps:

> **Bedrock normalizes → deterministic policy validates → user approves exact plan → bounded execution → receipts**

Under Bedrock, add small text:

> **no write authority · no spending choice**

Voiceover:

> “The language model does not decide how to spend money and never receives write authority. Deterministic policy chooses the repair, and material drift forces re-approval.”

Optionally flash one fail-closed state for two seconds:

> **Ambiguous provider state → execution blocked**

No diagram with more than these five concepts.

---

## 1:39–1:54 — Why this is a real Amazon build

Show a clean four-part technical proof panel, not a console walkthrough:

> **Alexa+ / MCP 2025-11-25** — public Streamable HTTP server
>
> **Amazon ECS Express / Fargate** — canonical public runtime
>
> **Amazon Bedrock / Nova 2 Lite** — changed-fact normalization
>
> **DynamoDB + CloudWatch** — durable authority + redacted trace evidence

Small proof footer:

> **OAuth + PKCE · authenticated remote smoke PASS · exact-SHA release proof**

Voiceover:

> “The experience is backed by a real public MCP 2025-11-25 server on AWS. Bedrock normalizes the changed fact, DynamoDB makes approval and receipts durable, and CloudWatch records redacted execution evidence.”

Do not show IAM screens, CloudShell, deployment logs or hashes unless one very short proof shot is aesthetically useful.

---

## 1:54–2:09 — Generality: Event Operations

Cut to a second, visually distinct Repair Card labelled:

> **EVENT OPERATIONS**

Show:

> **$5,800 at risk**
> **$620 repair**
> **$5,180 preserved**

Small subline:

> AV · catering · VIP transport · security · sponsor briefing

Voiceover:

> “Ripple is not a flight workflow. The same consequence-repair engine handles a conference-time change across AV, catering, VIP transport, security and sponsor commitments — and rejects a cheaper option when it preserves less value.”

Do not spend time explaining the full scenario.

---

## 2:09–2:23 — Real-world impact anchor

Use one restrained data card, clearly sourced:

> **2025 U.S. flight operations**
> **1.69M delayed arrivals**
> **118K cancellations**
> **Source: U.S. DOT Bureau of Transportation Statistics**

Voiceover:

> “The trigger is not hypothetical. U.S. DOT data shows disruption at massive scale. Ripple does not treat that as a market-size claim; it is the real stream of schedule changes on top of which downstream commitments break.”

Do not show percentages if they make the frame too busy. Do not imply every disruption becomes a Ripple repair event.

---

## 2:23–2:38 — Return to the customer outcome

Return to the original Repair Card after execution.

Show only:

> **5 commitments repaired**
> **$74 preserved**
> **0 duplicate writes**

Voiceover:

> “One cancellation. Five consequences. One bounded repair. The customer stays in control, and every effect is provable.”

---

## 2:38–2:42 — Memory anchor

Full-screen Ripple mark + tagline:

> **Tell Alexa one thing that changed.**
> **Ripple fixes what breaks downstream.**

Optional final micro-line:

> **One safe approval. Zero duplicate writes.**

No call-to-action beyond the tagline.

---

# Production direction

## Visual language

- 16:9, 1080p minimum;
- clean white/ivory background consistent with the real Ripple judge UI;
- large typography and generous whitespace;
- real Ripple UI as the primary visual asset;
- slow, deliberate zooms rather than frantic cursor movement;
- numbers `$116 / $42 / $74` and replay proof must be readable on a laptop without pausing;
- receipts should appear one by one to make execution tangible;
- no generic AI particles, neon brains, robots, stock footage or decorative cloud diagrams;
- no airline/provider logos unless rights are unquestionably safe;
- subtitles burned in, in English;
- voiceover should be calm, confident and human, not synthetic-advertising style.

## Audio

Prefer voiceover + very light original/licensed sound design.

Possible micro-cues:

- soft impact when the four economic metrics appear;
- subtle confirmation sound when approval occurs;
- five restrained receipt ticks;
- one quiet click when replay resolves to zero new writes.

Music is optional. If used, it must never compete with narration and must be licensed/original.

## Editing rules

- no shot longer than necessary;
- no terminal scrolling;
- no code editor as the main proof;
- no raw JSON unless used for a sub-second exact-SHA/7-of-7 proof insert;
- no architecture explanation before 1:23;
- no internal IDs in customer-facing shots;
- do not exceed 2:45 in the working cut; target 2:35–2:42 final;
- leave at least 15 seconds of safety margin under the 3:00 rule;
- the first 34 seconds must already prove the problem, the product and the economic outcome.

# Evidence and claim boundaries

The video may claim:

- canonical public AWS-hosted MCP runtime;
- MCP 2025-11-25 Streamable HTTP;
- OAuth/PKCE and authenticated remote smoke;
- Bedrock normalization;
- DynamoDB durable approval/receipts/replay;
- CloudWatch redacted trace evidence;
- exact approval;
- zero preapproval provider writes;
- five authoritative receipts;
- 5/5 replay deduplication and writes 5 → 5;
- seven executable adversarial scenarios passing in the frozen release;
- one bounded real GitHub Issues provider proof.

The video must **not** claim:

- real airline, ride, restaurant, grocery, pet-care or calendar production transactions;
- live market prices for the fixture dollar amounts;
- actual Alexa+ production-client use unless separately recorded from a successfully exercised official client;
- that BTS disruption counts equal Ripple addressable market;
- Railway as the current public runtime.

# Judge-score mapping

Every major beat must buy points:

- **0:00–0:34:** Design + Quality of Idea + customer comprehension
- **0:34–1:23:** Technical Implementation + trust + complete product loop
- **1:23–1:54:** Technical Implementation + Amazon ecosystem understanding
- **1:54–2:23:** Potential Impact + generality + credibility
- **2:23–2:42:** Design + memory/brand retention

The final cut is successful only if a judge can answer all four questions after one viewing:

1. What problem does Ripple solve?
2. Why is Alexa+ a natural interface for it?
3. Why is Ripple technically safer/deeper than a basic MCP wrapper?
4. Why could it matter beyond this hackathon?
