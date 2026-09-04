# Architecture v1.0

## Trust boundary

```text
Voice / simulated Alexa+
        |
        v
Change interpreter (LLM later; deterministic golden interpreter now)
        |
        v
ChangeEvent
        |
        v
DependencyEngine ---- read-only tool queries
        |
        v
Planner / option ranking
        |
        v
Deterministic ApprovalPolicy
        |
   explicit user approval
        |
        v
Executor (bounded saga + idempotency)
        |
        v
Simulated service adapters
        |
        v
ExecutionReceipts + reconciled plan status
```

The intelligence boundary is intentionally upstream of execution. A future Bedrock model may interpret language and rank valid repair options, but it cannot bypass policy or invoke writes directly.

## AWS target, not yet provisioned
- Bedrock/Strands: interpretation and option reasoning.
- DynamoDB: canonical graph, plan versions, approvals, idempotency ledger, receipts.
- Lambda/tool layer: bounded service adapters.
- CloudWatch: trace and failure evidence.

No AWS resource is provisioned until the local behavior is stable enough to justify the spend.

## Bedrock boundary v0.7
The production interpreter uses Nova 2 Lite client-side tool calling with a forced `record_change` tool. Model output is treated as untrusted input: node id, field, value and confidence are validated against canonical context. The model never supplies authoritative old values and never receives write authority.

## Judge-visible proof surface — v0.9
The local web simulation makes the trust boundary observable rather than implicit: dependency paths and costs are shown before approval; the exact snapshot hash and side-effect scope are disclosed; execution returns authoritative receipts; replay proves idempotency; and the executable adversarial matrix is available in the same surface.
