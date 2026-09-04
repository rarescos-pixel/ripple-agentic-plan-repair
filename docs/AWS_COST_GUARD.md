# AWS cost guard semantics

Ripple uses multiple cost controls rather than pretending AWS Budgets is a hard kill switch.

1. **Minimal scope** — Railway remains the MCP host; AWS is limited to Bedrock normalization, DynamoDB state and CloudWatch evidence.
2. **On-demand DynamoDB** — no provisioned read/write capacity.
3. **Bounded logs** — CloudWatch retention is 14 days and trace messages are size-limited.
4. **Application Inference Profile** — Bedrock usage is tagged to Ripple for attribution.
5. **Monthly budget alerts** — default $10/month with 50%, 80% and 100% actual-spend notifications.
6. **Benchmark before model lock** — model selection is quality-first, with token volume and latency as tie-breakers.
7. **Teardown script** — the AWS augmentation can be removed as one CloudFormation stack when no longer needed.

AWS Budgets notifications do **not** guarantee that Bedrock/DynamoDB/CloudWatch will stop at the budget amount. A true service cutoff would require a separate automated policy/action and could break the judge demo, so v1.5 intentionally uses alerts plus narrow architecture rather than an undisclosed kill switch.

The tag-scoped budget depends on activating the user-defined `Project` cost allocation tag in AWS Billing. Until activation and live verification, the budget is configuration-ready evidence, not a claimed active protection.
