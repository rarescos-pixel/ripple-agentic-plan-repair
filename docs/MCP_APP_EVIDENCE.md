# MCP App evidence boundary

What is executable in CI:
- exact `ui://` binding on `preview_repair_plan`;
- `resources/list` discovery;
- `resources/read` delivery;
- exact `text/html;profile=mcp-app` MIME;
- self-contained HTML payload;
- MCP App lifecycle markers;
- zero external network dependencies;
- no `tools/call`, approval-tool, or execution-tool authority in the widget;
- preview remains zero-write and leaves approval unset.

What CI does not claim:
- that Amazon Alexa+ Local Inspector has rendered the widget successfully;
- that Amazon certification has accepted the UX;
- that a specific Alexa device has displayed the card.

Those claims require live Amazon-side evidence after the server build is deployed.
