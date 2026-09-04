# v1.5 deployment environment map

| CloudFormation output | Railway variable |
|---|---|
| `StateTableName` | `RIPPLE_DYNAMODB_TABLE` |
| `TraceLogGroupName` | `RIPPLE_CLOUDWATCH_LOG_GROUP` |
| `TraceLogStreamName` | `RIPPLE_CLOUDWATCH_LOG_STREAM` |
| `BedrockApplicationInferenceProfileArn` | `RIPPLE_BEDROCK_MODEL_ID` |
| `RuntimePolicyArn` | attach to Railway AWS principal; not an env value |

Additional switches:

```text
RIPPLE_STATE_BACKEND=dynamodb
RIPPLE_CHANGE_INTERPRETER=bedrock
RIPPLE_TRACE_BACKEND=cloudwatch
AWS_REGION=eu-central-1
```

Do not enable these switches independently on the canonical service. Provision AWS, run preflight, then enable the complete set for a controlled smoke deployment so a partial configuration fails before judging traffic reaches it.
