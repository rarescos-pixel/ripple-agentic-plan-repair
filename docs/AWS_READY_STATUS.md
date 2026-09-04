# Ripple v1.5 — AWS-ready status

**Implementation state: AWS-ready verified.**

Canonical tested source SHA: `52bf87d245802e91b4c59aad1a369a285af87a4f`.

Independent GitHub Actions run `33875453562` passed:

- 64/64 full tests;
- 12/12 MCP 2025-11-25 + OAuth protocol tests;
- `cfn-lint infra/ripple-aws.json`;
- Release Gate v1.5;
- AWS Ready Gate v1.5;
- committed evidence drift check.

The same source SHA was deployed to the canonical Railway service with AWS switches disabled and passed an independent authenticated public MCP smoke. The smoke runner was then retired and server credentials were rotated.

Implemented and CI-verified: deployable IaC, DynamoDB backend configuration, Bedrock runtime switch, CloudWatch runtime switch, tagged Application Inference Profile cost attribution, project-tag budget configuration, constrained runtime IAM policy, live-capable normalization benchmark harness, deployment/teardown scripts, redacted trace contract and AWS readiness evidence.

**Not claimed:** live AWS stack, live Bedrock model result, live DynamoDB persistence, live CloudWatch trace, active tag-filtered budget, or Alexa+ production client. Those become verified only after real AWS provisioning and the live checklist passes.
