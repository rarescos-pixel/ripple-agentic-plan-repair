# AWS-ready DONE criterion

v1.5 is ready to merge when all local/CI capabilities are complete and independently verified without requiring an AWS account:

1. CloudFormation is syntactically/schema valid.
2. Core test suite and MCP/OAuth conformance remain green.
3. AWS readiness gate is green and evidence is committed with zero drift.
4. Bedrock runtime adapter and live benchmark harness are executable but make no CI network calls.
5. DynamoDB state backend remains restart-tested with local SQLite proof and fake DynamoDB contract tests.
6. CloudWatch trace sink is redaction-tested.
7. Default public runtime remains non-AWS until explicit env switches are enabled.
8. Deployment, environment mapping, budget caveats and teardown are documented.

Live AWS resource creation is deliberately outside this DONE criterion and becomes the next controlled verification stage.
