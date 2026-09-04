# Ripple — Pre-AWS Win Hardening v1.3

## Product position

**Tell Alexa one thing that changed. Ripple fixes what breaks downstream.**

Ripple is a **money-aware consequence-repair layer for Alexa+**. It turns one changed commitment into a dependency analysis, a bounded repair bundle, one exact approval, and verifiable receipts.

The primary customer promise is deliberately narrower than "AI assistant":

> Find what the change breaks, show the money/people/deadlines at risk, choose the repair that preserves the most value, and execute only after exact approval.

## What changed in v1.3

1. Economic selection now maximizes `avoidable_loss - added_cost` instead of minimizing sticker repair cost first.
2. Generic `changed_time_after_start` / `changed_time_after_end` dependency predicates prove the engine is not semantically tied to flights.
3. Legacy `arrival_after_*` predicates remain supported for backward compatibility.
4. A dependency node is marked visited only after its edge condition fires, preventing an earlier non-matching path from hiding a later valid path.
5. Simulated adapters can expose declarative repair options through the same `RepairOption` contract, allowing new domains to exercise the engine without hard-coding a new planner branch.
6. Added a money-heavy non-flight event-operations cascade: 5 impacts, $5,800 avoidable loss, $620 repair cost, $5,180 net preserved.
7. Automated baseline increases to **48 tests** and **7 executable adversarial/evidence scenarios**.

## What remains deliberately unchanged

- exact snapshot approval;
- zero writes in preview and approval;
- preflight-before-write;
- idempotent replay;
- public Streamable HTTP MCP transport;
- OAuth/PKCE boundary;
- five-tool public MCP surface;
- golden travel demo.

No random feature expansion is introduced.

## Next score-bearing work, in order

1. **Durable state:** DynamoDB for approvals/idempotency/receipts + restart-recovery proof.
2. **Alexa-first design:** one low-density inline Repair Card / MCP App-style surface with voice-only parity.
3. **Live AWS evidence:** one bounded Bedrock normalization call plus CloudWatch trace and least-privilege IAM; AWS must be structural evidence, not a decorative model call.
4. **Actual Alexa+ onboarding/client validation** if contestant access permits it.
5. **Demo/video:** lead with the customer consequence and money, not architecture.
6. **Real friction log:** only Amazon/Alexa/AWS friction actually encountered.

## 20-second judge story

> "Our flight was cancelled. We land tomorrow at six."
>
> Ripple: "Five commitments are affected. $116 is directly at risk. I can repair the cascade for $42 and preserve $74. That moves your ride and groceries, cancels the dinner before the fee, extends pet care, and moves the meeting with three people. Approve the $42 repair?"

Then show the compact consequence card and the five receipts. Architecture/evidence comes after the value is already obvious.
