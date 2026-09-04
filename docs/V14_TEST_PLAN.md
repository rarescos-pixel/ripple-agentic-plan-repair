# v1.4 test plan

Required gates:

1. Full pytest suite passes.
2. MCP 2025-11-25 + OAuth protocol suite passes unchanged.
3. Golden money metrics remain 116 / 42 / 74.
4. Restart test proves 2 pre-restart writes + 2 deduplicated + 3 new writes = 5 unique total.
5. DynamoDB adapter round-trips exact approval and authoritative receipt with a deterministic injected client.
6. Repair Card exposes only three primary economic metrics and at most three visible impacts.
7. Generated evidence files remain in sync.
