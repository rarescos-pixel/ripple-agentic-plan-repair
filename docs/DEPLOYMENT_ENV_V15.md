# v1.5 deployment environment map

| CloudFormation output | Railway variable |
|---|---|
| `StateTableName` | `RIPPLE_DYNAMODB_TABLE` |
| `TraceLogGroupName` | `RIPPLE_CLOUDWATCH_LOG_GROUP` |
| `TraceLogStreamName` | `RIPPLE_CLOUDWATCH_LOG_STREAM` |
| `BedrockApplicationInferenceProfileArn` | `RIPPLE_BEDROCK_MODEL_ID` |
| `RuntimePolicyArn` | attach to Railway AWS principal; not an env value |

Structural AWS switches:

```text
RIPPLE_STATE_BACKEND=dynamodb
RIPPLE_CHANGE_INTERPRETER=bedrock
RIPPLE_TRACE_BACKEND=cloudwatch
RIPPLE_REQUIRE_AWS_RUNTIME=true
AWS_REGION=eu-central-1
```

`RIPPLE_REQUIRE_AWS_RUNTIME=true` is the canonical Railway cutover lock. It makes startup/session construction fail closed unless all three structural AWS components are enabled together and the DynamoDB table, Bedrock application inference profile and CloudWatch log group bindings are present.

Production also rejects an accidental partial AWS profile even when the explicit lock is not set. The existing verified `memory + golden + no-op trace` profile remains valid until the controlled AWS cutover, so the public MCP is not destabilized merely by shipping this guard.

Do not enable the AWS switches independently on the canonical service. Provision AWS, run live preflight, bind the complete output set, enable the cutover lock, then run the authenticated remote smoke. This preserves the rule that AWS must be structural and demonstrable rather than cosmetic.
