# Ripple — live AWS verification checklist

Do not change `AWS-ready` to `AWS-live verified` until every item below has evidence tied to one source SHA.

- [ ] `cfn-lint infra/ripple-aws.json` PASS on the source SHA.
- [ ] CloudFormation stack reaches `CREATE_COMPLETE` or `UPDATE_COMPLETE`.
- [ ] Runtime policy is attached to the exact Railway AWS principal.
- [ ] Bedrock Application Inference Profile reports ACTIVE.
- [ ] Real Nova Lite vs Nova 2 Lite benchmark completed; winning model selected by documented policy.
- [ ] Real `record_change` through Bedrock returns a canonical ChangeEvent.
- [ ] Bedrock normalization performs zero repair/provider writes.
- [ ] Approval is present in DynamoDB before execution.
- [ ] New process/session can load the exact approval.
- [ ] New process/session deduplicates previously executed action receipts.
- [ ] CloudWatch receives `change.recorded`, `plan.previewed`, `plan.approved`, and `plan.executed` traces.
- [ ] Trace sample contains no secrets, tokens, passwords, cookies, API keys, or raw utterance.
- [ ] AWS Budget exists with 50/80/100% actual thresholds.
- [ ] `Project` user-defined cost allocation tag is activated in Billing before budget filter is relied upon.
- [ ] Public authenticated MCP smoke remains PASS after AWS switches are enabled.
- [ ] Credentials are rotated after test and absent from repository/log evidence.
- [ ] `docs/BEDROCK_BENCHMARK_LIVE.md` and live AWS evidence report are committed only after real calls.
