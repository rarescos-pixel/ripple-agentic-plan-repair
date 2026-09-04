# Devpost Submission Draft — v1.2 evidence-bounded

## Project name
Ripple

## Tagline
Tell Alexa one thing that changed. Ripple fixes what breaks downstream.

## One-sentence pitch
Ripple is a consequence-aware plan repair agent that turns one changed fact into a safe, approval-gated repair of every downstream commitment it actually affects.

## Problem
When plans change, the work rarely stays in one app. A cancelled flight can invalidate a ride, reservation, delivery window, care booking and meeting. The user must discover the cascade manually while already dealing with the original disruption.

## What Ripple does
Ripple normalizes one changed fact, traverses downstream dependencies, identifies only commitments now invalid or at risk, obtains bounded repair options, discloses cost/people/irreversible actions, waits for approval of the exact plan snapshot, executes idempotently, records authoritative receipts and leaves failures visibly unresolved.

Golden scenario: **5 downstream impacts, +$42 recovery cost, $116 direct loss avoidable, $74 net direct cash preserved.**

## Why Alexa+
This workflow is designed for divided-attention moments when opening five apps is the wrong interface. One utterance captures the changed fact; one compact proposal explains the cascade; one exact approval authorizes only that snapshot.

## Implemented and verified
- public self-hosted MCP Streamable HTTP endpoint using protocol `2025-11-25`;
- OAuth discovery, service client credentials, authorization-code + PKCE S256 user flow;
- five MCP tools: record, preview, approve, execute, status;
- deterministic dependency graph and five simulated service adapters;
- exact-content SHA-256 approval binding;
- preflight before writes, idempotency ledger and execution receipts;
- remote authenticated smoke from a separate Railway container: PASS;
- golden remote flow: 0 writes at preview, 0 at approval, 5 receipts at execute, 5/5 deduplicated on replay;
- local clean-room baseline: 43/43 tests, 12/12 MCP/OAuth tests, 6/6 adversarial scenarios, release gate PASS.

## Public runtime
`https://ripple-v12-production.up.railway.app/mcp`

## Disclosure
The MCP transport, OAuth surfaces, approval boundary, execution ledger and replay behavior are real running software. Calendar/Ride/Reservation/Delivery/Care adapters are deterministic simulators. No live AWS Bedrock invocation or real provider transaction is claimed yet.

## Next evidence-backed step
Add live AWS Bedrock + durable DynamoDB/Lambda/CloudWatch evidence only if it materially improves the rubric without destabilizing the verified MCP core.
