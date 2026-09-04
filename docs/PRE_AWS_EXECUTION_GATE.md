# Pre-AWS execution gate

Before spending AWS money:

- GitHub Actions v1.5 must be green.
- `cfn-lint` must pass.
- `AWS_READY_REPORT.md` must remain PASS with zero evidence drift.
- Public Railway v1.4 runtime must remain untouched until the v1.5 PR is promoted.
- Budget email and desired monthly threshold must be known.
- AWS credentials must be stored only in AWS/Railway secret storage.
- Bedrock benchmark must be limited to the five committed fixtures for the first run.
- No real provider adapters or payments are enabled during AWS activation.

If any item fails, do not provision live AWS yet.
