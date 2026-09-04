# Ripple Repair Card MCP App

Ripple exposes the existing `preview_repair_plan` decision surface as a self-contained MCP App resource.

Contract:
- tool binding: `preview_repair_plan._meta.ui.resourceUri`;
- resource URI: `ui://ripple/repair-card-dac4946046e5.html`;
- MIME type: `text/html;profile=mcp-app`;
- app protocol: `2026-01-26`;
- delivery: `resources/list` + `resources/read` over the existing authenticated MCP session;
- data source: the exact `structuredContent` returned by `preview_repair_plan`;
- external network access: none (`connectDomains=[]`, `resourceDomains=[]`);
- execution authority: none.

The widget is intentionally display-only. It does not call `tools/call`, does not contain the names of the approval or execution tools, and cannot persist approval or cause provider writes. The normal Ripple boundary remains unchanged:

`preview -> exact human approval -> deterministic policy validation -> bounded execution -> receipts`

The amount shown in the approval decision is supplied only by the exact preview payload. No approval amount is hard-coded into the widget.
