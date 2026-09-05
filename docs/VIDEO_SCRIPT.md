# Submission video script — judge-first target 2:35–2:45

The video must lead with customer value, not architecture. Do not show internal hashes, test matrices or AWS diagrams before the judge understands the product.

If an actual Alexa+ client is not available at recording time, label the shown web/Repair Card surface clearly as the **Alexa+ simulated experience backed by the real public MCP server**. Never imply an official Alexa session that did not happen.

## 0:00–0:20 — The whole product in one disruption

Show the user speaking / simulated Alexa+ prompt:

> “Our flight home was cancelled. We’ll land tomorrow at six.”

Immediately show the money-first Repair Card:

> **5 commitments are affected. $116 is at risk. Ripple can repair them for $42 and preserve $74. Approve $42 repair?**

Voiceover:

> “Plans rarely break one thing. Ripple repairs the consequences, not just the calendar.”

## 0:20–0:50 — Exact approval → visible outcome

Show the five human-readable affected commitments, then approve the exact $42 repair.

Show execution completing with five receipts.

Voiceover:

> “One spoken change becomes one bounded repair plan. Nothing is written before approval. The approval applies only to this exact cost, scope and notification set.”

Do **not** lead with snapshot hashes. They can appear briefly in technical evidence later if needed.

## 0:50–1:08 — Replay safety

Replay the same exact plan or reconnect in a fresh session.

Show:

- 5/5 actions deduplicated
- unique writes still 5
- duplicate provider writes: 0

Voiceover:

> “If a retry or restart happens, authoritative receipts stop duplicate writes.”

## 1:08–1:32 — Why this is a general consequence-repair layer

Switch briefly to Event Operations.

Show:

> **$5,800 at risk → $620 repair → $5,180 net preserved**

Voiceover:

> “This is not a flight workflow. The same engine repairs a conference-time change across AV, catering, VIP transport, security and sponsor commitments. It does not choose the cheapest action; it chooses the safe option that preserves the most net value.”

## 1:32–1:52 — The trust model

Use one simple architecture animation:

**language model normalizes → deterministic policy validates → user approves exact plan → bounded execution → receipts**

Voiceover:

> “The model never gets write authority and never decides how to spend money. Deterministic policy makes the economic choice and material drift forces re-approval.”

Show one failure state for only a few seconds: ambiguous provider or expired repair window stays unresolved instead of being fabricated as success.

## 1:52–2:12 — Alexa+ is real infrastructure, not a mock API

Show the live public MCP URL / inspector or evidence surface and the Repair Card MCP App.

On screen, keep only the judge-relevant proof:

- MCP 2025-11-25 / Streamable HTTP
- OAuth + PKCE
- MCP App Repair Card
- remote authenticated smoke: PASS
- store-media gate: PASS

Voiceover:

> “The public MCP server is live. OAuth, tool discovery, exact approval, execution and replay were exercised from a separate remote container. The Repair Card is a real MCP App resource, not a screenshot.”

## 2:12–2:30 — AWS structural proof

**Record this section only from the final frozen state.**

If AWS LIVE has passed, show the shortest possible evidence overlay:

- Bedrock normalized the spoken change
- DynamoDB preserved approval/receipts across a fresh session
- CloudWatch received the redacted trace
- replay remained 5/5 deduplicated

Voiceover:

> “AWS is structural: Bedrock only normalizes the changed fact, DynamoDB makes approval and receipts durable, and CloudWatch gives redacted evidence. Railway stays the public MCP host.”

If AWS LIVE has **not** passed, omit this section entirely rather than showing architecture as if it were live. Use the saved time for the customer outcome and remote MCP proof.

## 2:30–2:40 — Close

Return to the Repair Card and the $74 saved outcome.

> “One thing changed. Five commitments broke. Ripple repaired the cascade safely. Tell Alexa one thing that changed. Ripple fixes what breaks downstream.”

## Recording rules

- Keep the final cut under **3:00**; target under **2:45**.
- First value proposition must land within **20 seconds**.
- No terminal scrolling as the primary demo.
- No long dependency-graph explanation.
- Do not claim real airline/ride/reservation/delivery/care transactions: those adapters are deterministic simulations.
- Do not claim actual Alexa+ production-client use unless it is recorded from an exercised official client/onboarding path.
- Do not claim AWS live until the real AWS gate and Railway cutover pass.
- Prefer large numbers and human-readable commitment names over implementation identifiers.
