# Ripple v1.5 changeset

- Deployable CloudFormation for DynamoDB, CloudWatch Logs, Bedrock Application Inference Profile, IAM runtime policy and AWS Budget.
- Opt-in MCP runtime switches for Bedrock normalization and CloudWatch traces; v1.4 defaults remain unchanged.
- Structured `ripple.trace.v1` events with recursive secret redaction and bounded message size.
- Live-capable Nova Lite vs Nova 2 Lite normalization benchmark with five fixtures and quality-first selection policy.
- AWS deployment and teardown scripts.
- Deterministic AWS readiness report and IaC invariants.
- `cfn-lint` added to GitHub Actions.
- AWS SDK included in the deployable Railway image so AWS activation requires configuration, not a rebuild.
- Explicit disclosure that AWS-ready is not AWS-live verified.
