# First promise build gate — verified scope and remaining work

**Product selection remains closed.** This is implementation of Continuous
Promise Preservation, not a new product proposal or a claim of contest readiness.

## Verified result

- Baseline `cc6facb`: 127 tests passed before changes; all existing generated
  evidence and surface gates were reproducible.
- Local complete suite: **174 tests passed**, including the original 127;
  baseline surface/evidence gates and CloudFormation validation also pass.
- New core: versioned contract/world/plan, meaning confirmation, deterministic
  predicates, bounded minimal repair, immediate/future projection, authority
  envelope, expiry, explicit UNSATISFIABLE and a durable Promise Ledger.
- CAS persistence uses SQLite and the existing DynamoDB GetItem/PutItem substrate.
  The new DynamoDB adapter has contract tests; this is not live AWS evidence.
- The actual HTTP process-boundary build gate passes with **one contract version,
  four confirmed invariants, two verified writes and two independent receipts**.
- Five repeated executions produce **zero additional writes**. The checked
  execution transitions contain **zero invariant violations, zero unauthorized
  effects and zero unverified effects**.
- The worker observes events and reconciles independently of a conversational
  session. Reconstructing it from durable state preserves the same contract.
- New MCP mode is disabled by default. When enabled, it exposes only the promise
  workflow, so the old approval tool cannot be confused with the new authority
  model. MCP user tokens cannot access the
  separate human confirmation/approval route. Draft clarification is supported.
- A local human review experience is runnable after the core evidence gate.

Exact states, bindings, read-backs, receipts, projections and ledger hashes are in
[`PROMISE_BUILD_EVIDENCE.json`](PROMISE_BUILD_EVIDENCE.json). Metrics are calculated
from the run; no fixture asserts that a failed operation was successful.

## Canonical adversarial acceptance mapping

| Class | Executable evidence | Required behavior |
| --- | --- | --- |
| Assumption becomes false | `test_assumption_change_reprojects_before_failure` | Predict unsafe future plan while present state remains safe |
| Multiple assumptions change | `test_multiple_assumptions_changed_and_out_of_order_event`, hero | Accept coherent snapshot; reconcile without restating intent |
| Goal conflicts with invariant | `test_conflicting_goal_and_invariants_are_unsatisfiable` | Explicit bounded UNSATISFIABLE; no writes |
| Invariants conflict | `test_conflicting_invariants_are_not_silently_dropped` | No silent relaxation |
| Repair requires new authority | `test_new_repair_requires_new_authority` | Fresh exact approval |
| Stale approval | same test; `test_observe_immediately_invalidates_old_binding` | Reject before effects |
| Duplicate event | `test_duplicate_event_and_content_tamper` | No version rewind or duplicate processing |
| Replayed approval | `test_approval_replay_and_restart_do_not_repeat_writes` | No duplicate write |
| Out-of-order event | `test_multiple_assumptions_changed_and_out_of_order_event` | Preserve newest accepted world |
| False tool success | `test_false_tool_success_is_not_verified` | VERIFY_FAILED; block further effects |
| Goal becomes impossible | `test_impossible_goal_without_a_tool_is_explicit` | Explain finite-space impossibility |
| Minimal repair unsafe | `test_minimal_edit_candidate_is_unsafe_so_safe_larger_repair_wins` | Discard smaller unsafe repair |
| Equivalent repairs | `test_cheapest_unsafe_repair_is_excluded_and_tie_is_stable` | Stable deterministic result |
| Expiry during execution | `test_expiry_at_provider_commit_prevents_effect`, conditional-expiry test | Guard at provider commit, not just before request |
| Misinterpreted intent | semantic ambiguity/revision tests, clarification/low-confidence tests | No ACTIVE meaning until human confirmation; corrected version invalidates old authority |

Additional tests exercise crash after effect/before receipt, concurrent workers,
provider revision races, time-dependent guards, unknown facts, type confusion,
capacity limits, search limits, owner isolation, catalogue drift, three domains,
goal maintenance after its deadline, ledger hashes and session-independent MCP.

## Corrections discovered during implementation

1. Mom leaving cannot revoke her access. The unconditional access invariant stays.
2. A scheduled departure is not proof of occupancy. Full security and Away need
   independently observed family departure, including at the commit boundary.
3. A late first attempt cannot silently move a missed deadline. A goal that was
   already achieved, however, remains under reconciliation until terminal state.
4. An observed world change invalidates the approval binding immediately, even
   before the next planner invocation.
5. Missing goal evidence is clarification, never an invented impossibility proof.
6. Effects already accomplished by an independent world change are removed from
   the proposal, preventing an unnecessary repeat write.

## Remaining release gates — not yet PASS

| Gate | Concrete completion evidence |
| --- | --- |
| Live Bedrock intent normalization | Real model output for the hero and ambiguous/corrected intents; validated contracts and human review, no canned normalization |
| Live AWS persistence and traces | New promise keys, CAS/restart behavior and CloudWatch events from an isolated runtime at the exact feature SHA |
| Alexa+ host experience | Account-linked real session, tool discovery, meaningful clarification, cross-session status and the separate approval handoff demonstrated on the target host |
| Real device/provider semantics | Verified adapter capabilities and independent physical/provider read-back; otherwise explicitly submit as a digital-twin demonstration |
| New sub-three-minute video | Actual new flow captured; distinguish live operations, twin facts and normalization fixtures on screen |
| Final submission/evaluator audit | README/add-on/submission/video aligned to the new product; evidence for all four criteria without claiming best-in-field or a win probability |

The existing AWS deploy workflows are tied to canonical `main` and contain live
infrastructure mutations. This feature branch does not edit or run those workflows,
alter IAM trust, migrate tables, merge itself or activate the new path in production.
The old polished video and AWS evidence remain baseline assets, not proof that the
new product has passed these release gates.

## Next implementation order

1. Verify this branch's full CI and review the exact delta.
2. Run the new normalization and durability path in an isolated AWS environment;
   resolve any real model ambiguity before collecting the hero recording.
3. Verify the target Alexa host and chosen conditional provider. Preserve the
   current safe failure behavior wherever a provider lacks atomic guarantees.
4. Capture the 2:45 demonstration below, update submission surfaces and run the
   final rubric audit. Do not expand into another product direction.

## 2:45 recording plan

| Time | Judge-visible result |
| --- | --- |
| 0:00–0:20 | One human instruction; plain-language meaning confirmation and four things to preserve |
| 0:20–0:40 | Why whole-house Away would violate the intent; exact partial transition proposal |
| 0:40–1:10 | Mom goes out; the same contract changes its plan while retaining access; fresh approval and independent read-back |
| 1:10–1:40 | Departure moves; predicted violation highlighted before the old transition fires; smallest safe repair |
| 1:40–2:10 | Actual family departure evidence; approved effect, read-back, receipts; explicitly label provider scope |
| 2:10–2:30 | New session/worker recovery and five replays without another write |
| 2:30–2:45 | Measured outcome and one sentence on generic reuse; compact evidence link |

Use real measured results from the recorded run. Human confirmation, action
approvals and independently observed events are interactions; “one instruction”
must never be presented as “one total interaction.”
