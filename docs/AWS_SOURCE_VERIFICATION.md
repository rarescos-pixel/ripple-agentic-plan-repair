# AWS API assumptions verified for v1.5

Verified against current AWS documentation on 2026-09-04 before implementation:

- Bedrock `Converse` accepts model IDs and inference profile identifiers.
- Nova Lite EU geo inference ID: `eu.amazon.nova-lite-v1:0`.
- Nova 2 Lite EU geo inference ID: `eu.amazon.nova-2-lite-v1:0`.
- `AWS::Bedrock::ApplicationInferenceProfile` is supported by CloudFormation and can carry tags for Bedrock cost attribution.
- DynamoDB CloudFormation supports `PAY_PER_REQUEST` and point-in-time recovery.
- CloudWatch Logs `PutLogEvents` ignores sequence tokens; v1.5 does not implement obsolete token chaining.
- AWS Budgets supports actual-spend thresholds and email subscribers.
- Tag-filtered budgets require the user-defined cost allocation tag to be activated before the filter can be relied upon.

This file records implementation assumptions, not live-resource evidence.
