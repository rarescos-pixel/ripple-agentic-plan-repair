# Ripple — MASTER v1.2

## Product lock
**Tell Alexa one thing that changed. Ripple fixes what breaks downstream.**

Ripple is a consequence-aware plan repair agent. It represents commitments as a dependency graph, propagates a changed fact to downstream impacts, constructs the smallest safe repair plan, discloses money and external side effects, and performs bounded idempotent writes only after explicit approval.

## Safety invariant — LOCKED
**LLM proposes → deterministic policy validates → user approves the exact content snapshot → bounded tools execute → receipts are authoritative.**

## Canonical entities
`PlanNode` / `DependencyEdge` / `ChangeEvent` / `Impact` / `RepairOption` / `RepairAction` / `RepairPlan` / `Approval` / `ExecutionReceipt`.

## Acceptance gates — VERIFIED
1. Golden cascade detects exactly 5 impacts.
2. Financial summary: +$42, $116 avoidable direct loss, $74 net direct cash preserved.
3. Exactly 5 bounded external actions.
4. Preview and approval perform zero writes.
5. Approval binds to exact plan id/version/content hash/cost/scope.
6. Ambiguous provider state blocks before the first write.
7. Replay and interrupted recovery produce zero duplicate external writes.
8. Provider failure stays truthful/partial.
9. Missed deadlines remain unresolved rather than fabricated as saved.
10. Hard user constraints filter options before cost optimization.
11. Intermediate fact nodes are traversed without invented actions.
12. Unaffected commitments are not repaired.

Local clean-room proof: **43/43 tests, 12/12 MCP/OAuth, 6/6 adversarial scenarios, release gate PASS.**

## Public MCP — VERIFIED
- Base: `https://ripple-v12-production.up.railway.app`
- MCP: `https://ripple-v12-production.up.railway.app/mcp`
- Protocol: `2025-11-25` Streamable HTTP.
- OAuth discovery + client credentials + authorization-code/PKCE S256.
- Five tools: `record_change`, `preview_repair_plan`, `approve_repair_plan`, `execute_repair_plan`, `get_repair_status`.
- Independent remote runner: PASS.
- Remote semantics: 5 impacts → 0 preview writes → 0 approval writes → 5 receipts / 5 unique writes → replay 5/5 deduplicated.

## Current limitations — explicit
- five downstream service adapters are deterministic simulators;
- OAuth/token/session/idempotency state is in-memory and single-instance;
- no actual Alexa+ production client onboarding has been claimed;
- no live AWS Bedrock/Lambda/DynamoDB/CloudWatch runtime has been claimed.

## AWS next boundary
Only evidence-backed expansion: one constrained Bedrock/Nova call for `record_change`, Lambda deterministic boundary, DynamoDB durability, CloudWatch trace. No additional AWS service without a concrete rubric gain or defect.

## Unlock rule
Do not reopen product discovery unless a near-identical competitor invalidates differentiation, rules make Ripple ineligible, or a material technical blocker destroys the demo.
