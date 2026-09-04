# Minimal live AWS scope

The AWS milestone is deliberately narrow. Ripple already has a public MCP endpoint; live AWS exists to prove durable state and a real model boundary, not to replace working infrastructure.

## Required live evidence

1. DynamoDB table receives an exact approval and authoritative execution receipt.
2. Restart/retry path reads the persisted receipt and prevents a duplicate external write.
3. Bedrock receives only the bounded change-normalization payload and returns a structured `ChangeEvent` proposal.
4. Deterministic policy rejects malformed/out-of-contract model output.
5. CloudWatch records structured traces for normalization, approval persistence and execution.
6. Runtime IAM has only the required DynamoDB/Bedrock/log permissions.
7. AWS Budget alarm exists before any load test.

## Explicit non-goals

- moving the MCP server off Railway without a measured benefit;
- using Bedrock to decide costs or side effects;
- adding AgentCore only for branding;
- provisioning multiple databases;
- creating real airline/ride/reservation integrations before judging value is proven.
