# AWS readiness — cost-efficient integration v1.2

## Decision
Use AWS only where it increases hackathon evidence. The public MCP runtime and deterministic core are already verified; AWS must not weaken them.

## Minimal target stack
1. **Amazon Bedrock / Nova 2 Lite** — one constrained inference per reported change, forced to `record_change` tool calling.
2. **AWS Lambda** — thin boundary around the deterministic Ripple engine/tool layer.
3. **DynamoDB** — durable canonical graph, plan snapshot, approval, idempotency ledger and receipts.
4. **CloudWatch** — structured traces for golden, blocked-write and recovery evidence.

No AgentCore, Step Functions, Knowledge Base, vector database, provisioned model throughput or always-on compute unless a measured rubric gap requires it.

## Cost controls
- on-demand Bedrock only;
- one model call per proposal;
- temperature 0, max 256 output tokens;
- application-owned old state and allowlisted node/field context;
- no provisioned Lambda concurrency;
- one small DynamoDB Standard table for the prototype;
- short CloudWatch retention and no full prompt logging by default;
- AWS Budget alarm before repeated evaluation runs.

## Current verified boundary
The Bedrock `Converse` adapter is implemented and fake-client tested. No live Bedrock/Lambda/DynamoDB/CloudWatch runtime claim is made yet. The public Railway MCP endpoint remains the canonical Alexa+ integration proof until AWS runtime evidence exists.
