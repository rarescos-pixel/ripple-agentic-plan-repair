# Ripple pre-AWS promotion gate

Do not provision AWS resources until all of the following are green:

- full test suite;
- MCP 2025-11-25 + OAuth conformance suite;
- money-aware ranking scenarios;
- exact approval drift tests;
- restart durability test;
- Repair Card contract test;
- generated evidence drift check;
- public MCP remote smoke on the promoted commit.

Only after this gate passes should live AWS work begin. The live AWS milestone is limited to the minimum high-value evidence: DynamoDB durability, one real Bedrock normalization path, CloudWatch traces, least-privilege IAM and a budget alarm. Hosting remains on the already cheap Railway MCP unless a measured reason justifies migration.
