from __future__ import annotations

from ripple.presentation.mcp_app import (
    MCP_APP_MIME_TYPE,
    MCP_APP_PROTOCOL_VERSION,
    REPAIR_CARD_APP_HTML,
    REPAIR_CARD_RESOURCE_URI,
    repair_card_resource_contents,
    repair_card_resource_descriptor,
)


def main() -> None:
    descriptor = repair_card_resource_descriptor()
    contents = repair_card_resource_contents()
    assert REPAIR_CARD_RESOURCE_URI.startswith("ui://")
    assert descriptor["uri"] == contents["uri"] == REPAIR_CARD_RESOURCE_URI
    assert descriptor["mimeType"] == contents["mimeType"] == MCP_APP_MIME_TYPE
    assert MCP_APP_MIME_TYPE == "text/html;profile=mcp-app"
    assert MCP_APP_PROTOCOL_VERSION == "2026-01-26"
    assert contents["text"] == REPAIR_CARD_APP_HTML
    assert "tools/call" not in REPAIR_CARD_APP_HTML
    assert "approve_repair_plan" not in REPAIR_CARD_APP_HTML
    assert "execute_repair_plan" not in REPAIR_CARD_APP_HTML
    assert "fetch(" not in REPAIR_CARD_APP_HTML
    assert "XMLHttpRequest" not in REPAIR_CARD_APP_HTML
    assert "WebSocket" not in REPAIR_CARD_APP_HTML
    print("Ripple MCP App static safety gate: PASS")
    print("resource:", REPAIR_CARD_RESOURCE_URI)
    print("mime:", MCP_APP_MIME_TYPE)
    print("protocol:", MCP_APP_PROTOCOL_VERSION)


if __name__ == "__main__":
    main()
