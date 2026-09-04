# Repair Card MCP App test plan

Required before merge:

1. Full repository test suite passes.
2. Existing MCP 2025-11-25 protocol suite still passes unchanged.
3. MCP App contract suite passes exact URI, MIME, resource discovery/read, tool binding, preview-result binding, and zero-write semantics.
4. Static safety gate proves the widget has no tool-call or external-network authority.
5. Generated evidence files show zero drift.
6. After merge, production deployment must pass the existing authenticated remote MCP smoke before any Alexa-side claim is made.
