from __future__ import annotations

MCP_APP_PROTOCOL_VERSION = "2026-01-26"
MCP_APP_MIME_TYPE = "text/html;profile=mcp-app"
REPAIR_CARD_RESOURCE_URI = "ui://ripple/repair-card-dac4946046e5.html"


REPAIR_CARD_APP_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ripple Repair Card</title>
<style>
:root{
  color-scheme:light dark;
  font-family:var(--font-sans,Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif);
  --bg:var(--color-background-primary,#ffffff);
  --text:var(--color-text-primary,#171a22);
  --muted:var(--color-text-secondary,#667085);
  --border:var(--color-border-primary,#dfe3ea);
  --panel:var(--color-background-secondary,#f8fafc);
  --accent:var(--color-accent-primary,#171a22)
}
*{box-sizing:border-box}
body{margin:0;background:transparent;color:var(--text)}
main{width:100%;padding:16px}
.card{background:var(--bg);border:1px solid var(--border);border-radius:18px;padding:18px;box-shadow:0 6px 24px rgba(20,24,35,.06)}
.eyebrow{font-size:.72rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;color:var(--muted)}
h1{font-size:1.55rem;line-height:1.15;letter-spacing:-.03em;margin:5px 0 4px}
.sub{margin:0 0 14px;color:var(--muted);font-size:.93rem}
.money{font-weight:800;font-size:1rem;margin:0 0 14px}
.metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:12px 0 15px}
.metric{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:11px}
.metric b{display:block;font-size:1.25rem;letter-spacing:-.03em}
.metric span{display:block;margin-top:2px;font-size:.72rem;color:var(--muted)}
.impacts{display:grid;gap:7px;margin:11px 0}
.impact{display:flex;justify-content:space-between;gap:10px;border-bottom:1px solid var(--border);padding:8px 0}
.impact:last-child{border-bottom:0}
.label{font-weight:700;font-size:.92rem}
.cash{font-variant-numeric:tabular-nums;color:var(--muted);white-space:nowrap}
.scope{font-size:.82rem;color:var(--muted);margin:11px 0}
.voice{margin:13px 0 0;padding:12px;border-left:3px solid var(--accent);background:var(--panel);border-radius:0 10px 10px 0;font-size:.9rem;line-height:1.42}
.decision{margin-top:14px;width:100%;border-radius:12px;padding:12px 14px;text-align:center;font-weight:800;background:var(--accent);color:var(--bg);border:1px solid var(--accent)}
.note{font-size:.72rem;color:var(--muted);text-align:center;margin:7px 0 0}
.empty{color:var(--muted);padding:12px 0}
@media(max-width:420px){main{padding:10px}.card{padding:15px}.metrics{gap:6px}.metric{padding:9px}.metric b{font-size:1.08rem}}
</style>
</head>
<body>
<main>
<section class="card" aria-live="polite" aria-label="Ripple repair plan">
  <div class="eyebrow">Ripple · consequence repair</div>
  <div id="content"><div class="empty">Repair plan ready.</div></div>
</section>
</main>
<script>
(() => {
  const APP_PROTOCOL = "2026-01-26";
  const APP_ID = 1;
  let initialized = false;
  let hostContext = {};

  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[c]));

  const send = (message) => window.parent.postMessage(message, "*");

  const notifySize = () => {
    const body = document.documentElement;
    send({
      jsonrpc: "2.0",
      method: "ui/notifications/size-changed",
      params: {
        width: Math.ceil(body.scrollWidth),
        height: Math.ceil(body.scrollHeight)
      }
    });
  };

  const applyHostContext = (context) => {
    hostContext = {...hostContext, ...(context || {})};
    const theme = hostContext.theme;
    if (theme === "dark" || theme === "light") document.documentElement.style.colorScheme = theme;
    const vars = hostContext.styles && hostContext.styles.variables;
    if (vars && typeof vars === "object") {
      for (const [key, value] of Object.entries(vars)) {
        if (typeof value === "string" && key.startsWith("--")) {
          document.documentElement.style.setProperty(key, value);
        }
      }
    }
  };

  const parsePayload = (params) => {
    if (params && params.structuredContent && typeof params.structuredContent === "object") {
      return params.structuredContent;
    }
    const blocks = params && Array.isArray(params.content) ? params.content : [];
    for (const block of blocks) {
      if (block && block.type === "text" && typeof block.text === "string") {
        try {
          const parsed = JSON.parse(block.text);
          if (parsed && typeof parsed === "object") return parsed;
        } catch (_) {}
      }
    }
    return null;
  };

  const render = (payload) => {
    const card = payload && payload.repair_card;
    const root = document.getElementById("content");
    if (!card || typeof card !== "object") {
      root.innerHTML = '<div class="empty">No repair proposal to display yet.</div>';
      notifySize();
      return;
    }

    const metrics = Array.isArray(card.metrics) ? card.metrics.slice(0, 3) : [];
    const impacts = Array.isArray(card.top_impacts) ? card.top_impacts : [];
    const scope = card.scope || {};
    const remaining = Number(card.remaining_impacts || 0);
    const decision = card.decision || {};

    root.innerHTML = `
      <h1>${esc(card.headline || "Repair plan")}</h1>
      <p class="sub">${esc(card.subheadline || "")}</p>
      <p class="money">${esc(card.money_summary || "")}</p>
      <div class="metrics">
        ${metrics.map(m => `<div class="metric"><b>${esc(m.value)}</b><span>${esc(m.label)}</span></div>`).join("")}
      </div>
      <div class="impacts" aria-label="Top affected commitments">
        ${impacts.map(i => `<div class="impact"><span class="label">${esc(i.label || i.id)}</span><span class="cash">${esc(i.cash_at_risk || "")}</span></div>`).join("")}
      </div>
      ${remaining > 0 ? `<div class="scope">+${remaining} more affected commitment${remaining === 1 ? "" : "s"}</div>` : ""}
      <div class="scope">${esc(scope.actions || 0)} bounded actions · ${esc(scope.services || 0)} services · ${esc(scope.people_notified || 0)} people notified</div>
      <div class="voice">${esc(card.voice_summary || "")}</div>
      <div class="decision" role="note" aria-label="${esc(card.accessibility_label || decision.label || "Approval required")}">${esc(decision.label || "Approval required")}</div>
      <p class="note">No changes occur until Alexa receives explicit approval for this exact plan.</p>
    `;
    notifySize();
  };

  window.addEventListener("message", (event) => {
    if (event.source !== window.parent) return;
    const msg = event.data;
    if (!msg || msg.jsonrpc !== "2.0") return;

    if (msg.id === APP_ID && msg.result && !initialized) {
      initialized = true;
      applyHostContext(msg.result.hostContext || {});
      send({jsonrpc:"2.0", method:"ui/notifications/initialized", params:{}});
      notifySize();
      return;
    }

    if (msg.method === "ui/notifications/tool-result") {
      render(parsePayload(msg.params || {}));
      return;
    }

    if (msg.method === "ui/notifications/host-context-changed") {
      applyHostContext(msg.params || {});
      notifySize();
      return;
    }

    if (msg.method === "ui/resource-teardown" && Object.prototype.hasOwnProperty.call(msg, "id")) {
      send({jsonrpc:"2.0", id:msg.id, result:{}});
    }
  });

  if ("ResizeObserver" in window) {
    const observer = new ResizeObserver(() => {
      if (initialized) notifySize();
    });
    observer.observe(document.documentElement);
  }

  send({
    jsonrpc:"2.0",
    id:APP_ID,
    method:"ui/initialize",
    params:{
      protocolVersion:APP_PROTOCOL,
      appInfo:{name:"Ripple Repair Card",version:"1.5.0"},
      appCapabilities:{availableDisplayModes:["inline"]}
    }
  });
})();
</script>
</body>
</html>'''


def repair_card_resource_descriptor() -> dict[str, object]:
    return {
        "uri": REPAIR_CARD_RESOURCE_URI,
        "name": "Ripple Repair Card",
        "description": "Money-first Alexa+ decision surface for an exact Ripple repair proposal.",
        "mimeType": MCP_APP_MIME_TYPE,
        "_meta": {
            "ui": {
                "prefersBorder": True,
                "csp": {"connectDomains": [], "resourceDomains": []},
            }
        },
    }


def repair_card_resource_contents() -> dict[str, object]:
    return {
        "uri": REPAIR_CARD_RESOURCE_URI,
        "mimeType": MCP_APP_MIME_TYPE,
        "text": REPAIR_CARD_APP_HTML,
        "_meta": {
            "ui": {
                "prefersBorder": True,
                "csp": {"connectDomains": [], "resourceDomains": []},
            }
        },
    }
