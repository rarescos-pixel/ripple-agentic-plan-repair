# Ripple v1.4 candidate status

Candidate scope:

- restart-durable approval and receipt contract;
- SQLite executable restart proof;
- DynamoDB adapter with injected-client tests;
- Alexa-first low-density Repair Card builder;
- no change to the already verified MCP transport or approval hash contract;
- no live AWS claim.

Promotion rule: merge only after independent GitHub Actions passes the full suite, MCP/OAuth protocol suite and evidence drift check.
