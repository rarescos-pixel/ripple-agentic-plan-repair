# Ripple VIDEO FREEZE PACKET

Fill this only when the product is ready to be filmed. Do not infer missing fields.

## 1. Build identity

- VIDEO-READY git SHA:
- branch/ref:
- commit message:
- live URL:
- deployment/revision identity:
- date/time frozen (timezone):

## 2. Golden scenario — exact verified state

### User change
- exact user utterance/input:
- previous state:
- new state:

### Dependency analysis
- exact number of impacts:
- impact labels:

### Economics
- total at risk:
- repair cost:
- value preserved:
- calculation/evidence source:

### Approval
- exact approval object/plan identity:
- what changes invalidate approval and require reapproval:

### Execution
- exact intended writes/actions:
- exact number of successful receipts:
- exact number of people notified:
- expected replay behavior:
- duplicate writes expected on replay:

## 3. Capture path

For every shot, record the exact interaction sequence and expected observable state.

1.
2.
3.
4.
5.

Automation/capture command or test reference:

## 4. VERIFIED platform claims

Mark each AVAILABLE / VERIFIED WORKING / DEGRADED / INVALIDATED / UNKNOWN and attach evidence.

- public demo:
- source revision endpoint:
- MCP Streamable HTTP:
- OAuth 2.1 / PKCE:
- Alexa+ simulation:
- Alexa+ official Local Inspector:
- Alexa+ add-on deployment/entitlement:
- AWS structural runtime:
- DynamoDB durable state:
- Bedrock:
- CloudWatch:
- external real provider integration:
- external MCP latency requirement:

## 5. Claims explicitly forbidden in the video

List anything not independently verified or no longer true.

-
-
-

## 6. Evidence files / URLs / workflow runs

Only public or judge-usable evidence should appear in the final video/description. Never include credentials, private auth URLs, tokens, session state, account identifiers, or secret-bearing logs.

-
-
-

## 7. UI freeze

- capture viewport:
- product theme/state:
- seed/reset procedure:
- browser/version if relevant:
- no-debug-overlay check:
- no-private-data check:

## 8. Final pre-capture gate

All must be YES:

- [ ] exact source revision identified
- [ ] deployed build matches source revision
- [ ] golden flow passes end-to-end
- [ ] zero writes before approval proven
- [ ] receipts proven after approval
- [ ] replay/deduplication proven
- [ ] economics values independently verified
- [ ] all on-screen platform claims have evidence
- [ ] forbidden claims documented
- [ ] capture can be reset and reproduced
- [ ] no sensitive values can appear in footage

If any required box is NO, the product is not VIDEO-READY.
