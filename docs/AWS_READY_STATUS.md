# v1.5 status before independent CI

**Implementation state:** AWS-ready candidate.

Implemented: deployable IaC, DynamoDB backend configuration, Bedrock runtime switch, CloudWatch runtime switch, Application Inference Profile cost attribution, project-tag budget, least-privilege managed policy, benchmark harness, deployment/teardown scripts, local contract tests and AWS readiness gate.

Not claimed: live AWS stack, live Bedrock model result, live DynamoDB restart, live CloudWatch trace, active tag-filtered budget, or Alexa+ production client.

Promotion requires independent PR CI PASS.
