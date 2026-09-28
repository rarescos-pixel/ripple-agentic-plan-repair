# Continuous Promise Preservation — implementation contract

Canonical direction: the 2026-09-27 handoff. Product selection is closed.

## Verified baseline (before edits)

- Base: `cc6facb9e0b45f164c5cc78b403ece6150f5c989` on remote `main`.
- No published release or open PR was present at read-back.
- Clean Python 3.12 environment: `PYTHONPATH=src python -m pytest -q`:
  **127 passed**, one upstream Starlette deprecation warning.
- Existing MCP App, Alexa add-on, submission surface, matrix, adversarial,
  cost benchmark, release and AWS structural gates: **PASS**, no generated diff.
- Remote baseline CI: https://github.com/rarescos-pixel/ripple-agentic-plan-repair/actions/runs/36305736684
- This is a source/test baseline, not a new probe of the deployed AWS service.

## Minimum delta

Add an isolated `ripple.promises` package. Preserve the existing five MCP tools,
planner, approval policy, durable receipts, AWS runtime and evidence suites.
The existing money-oriented planner selects repairs independently; it cannot
enforce cross-action invariants. The new bounded planner therefore shares the
runtime and providers, not that selection algorithm.

| Existing asset | Added responsibility |
| --- | --- |
| Bedrock normalization | Propose a validated draft contract; never decide truth or confer authority |
| Exact approval | Bind contract/world/plan versions and exact delta; separate human channel |
| DynamoDB GetItem/PutItem | Separate promise keys, conditional aggregate revision; no table migration |
| Receipts/replay | Durable execution reservation, provider idempotency, independent read-back |
| CloudWatch trace sink | Redacted lifecycle metadata; durable ledger remains authoritative |
| MCP 2025-11-25 | Opt-in promise tools; no model-accessible confirmation/approval operation |

## Semantics

- A contract has goal, invariants, assumptions, authority, expiry and evidence.
  A draft cannot act. Confirmation acknowledges its exact meaning/hash/version.
- Assumptions are observations to re-evaluate, never permissions or invariants.
  An absent occupant does **not** lose an invariant protecting their access.
- The expression language is finite, typed, deterministic and rejects unknown
  operators. Missing/stale facts yield clarification, not invented truth.
- Goals and invariants are checked against each projected intermediate state
  and the declared goal time. The current plan is re-projected on every accepted
  world snapshot, even before a scheduled effect is due.
- Planning enumerates a bounded, deployment-owned action catalogue. Among valid
  plans, minimize edits to the remaining plan, then writes, then a stable tie
  break. `UNSATISFIABLE` means no plan in this **declared bounded action space**;
  an exhausted search budget or missing evidence is not a proof of impossibility.
- Provider snapshots have a single monotonic revision and content-bound event
  ID. Duplicates are no-ops; out-of-order snapshots cannot rewind state.
- Approval binds owner, contract version/hash, world version, plan version/hash
  and exact actions. Every accepted world change invalidates old authority.
  After a verified write, any remaining plan is reconciled and needs fresh
  consequential approval. No implicit inheritance across repairs.
- OBSERVE never writes; AUTONOMOUS_REVERSIBLE requires both explicit confirmed
  contract permission and a deployment-declared reversible control;
  APPROVAL_REQUIRED requires exact human approval; FORBIDDEN cannot be planned.
- An execution reservation is persisted with compare-and-swap before provider
  I/O. Recovery uses the same key. Providers must enforce expected revision,
  idempotency and expiry at their write boundary. An HTTP 200 is not verification.
- No provider success claim without an independent read matching the declared
  effect and all invariants. Unknown/partial outcomes block further effects.
- ACTIVE continues after a successful action. SATISFIED requires the explicit
  completion predicate plus goal/invariant evidence. EXPIRED, REVOKED and
  UNSATISFIABLE are terminal. Contract revision returns to meaning confirmation.

## Scope of the first evidence gate

The initial provider is a separate HTTP service with SQLite-backed world state,
conditional transactions and its own durable idempotency journal. It proves real
process-boundary writes, restart and independent read-back. Its household facts
are a **digital twin**, not physical Alexa/Ring/thermostat control. Do not label
this as a live smart-home deployment. Production device adapters must implement
the same safety boundary before activation.

The aggregate and search space are deliberately bounded. Capacity limits fail
closed before a write. A worker receives an explicit deployment watchlist of
contract IDs through a bounded durable watchlist and rehydrates their state; no DynamoDB Scan or new
IAM permission is necessary. This is not an unbounded multi-tenant scheduler.

## Tests before implementation

The acceptance suite covers all 15 canonical adversarial classes, plus expiry
at the provider commit boundary, concurrency/restart, separate human authority,
three-domain reuse, unknown facts, bounded search and storage capacity. Evidence
includes exact bindings, before/after snapshots, read-back, ledger transitions
and provider write counts. A successful concept or assertion is not gate PASS.

Execution conditions in the deployment catalogue are checked against independently
observed state at both reservation and provider commit. Future projection is
conditional on these prerequisites; it is never proof that occupants departed.
Deadline satisfaction is recorded as evidence. After a goal was actually met,
reconciliation continues until explicit completion or expiry; a later drift does
not erase that evidence or silently reclassify the original deadline.

## Build order

1. Failing behavioral acceptance tests.
2. Deterministic model/planner, versioned lifecycle and durable CAS stores.
3. Conditional provider, independent verification and recovery.
4. Continuous worker, isolated MCP/human interface and Bedrock draft boundary.
5. Executable hero evidence and all baseline gates; publish an isolated PR.
6. Alexa/device integration and presentation follow the proven core. Deployment
   remains a separate operation; this branch must not silently alter production.
