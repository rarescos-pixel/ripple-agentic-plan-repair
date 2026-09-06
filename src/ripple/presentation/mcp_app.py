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
.impacts,.receipts{display:grid;gap:7px;margin:11px 0}
.impact,.receipt{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;border-bottom:1px solid var(--border);padding:8px 0}
.impact:last-child,.receipt:last-child{border-bottom:0}
.label{font-weight:700;font-size:.92rem}
.cash{font-variant-numeric:tabular-nums;color:var(--muted);white-space:nowrap}
.scope{font-size:.82rem;color:var(--muted);margin:11px 0}
.why{margin:13px 0 0;padding:12px;background:var(--panel);border:1px solid var(--border);border-radius:11px;font-size:.84rem;line-height:1.42}
.why b{display:block;margin-bottom:3px}
.why .specific{display:block;color:var(--muted);margin-top:5px}
.voice{margin:13px 0 0;padding:12px;border-left:3px solid var(--accent);background:var(--panel);border-radius:0 10px 10px 0;font-size:.9rem;line-height:1.42}
.decision{margin-top:14px;width:100%;border-radius:12px;padding:12px 14px;text-align:center;font-weight:800;background:var(--accent);color:var(--bg);border:1px solid var(--accent)}
.proof{font-size:1rem;font-weight:800;margin:12px 0}
.status{text-transform:uppercase;letter-spacing:.06em;font-size:.66rem;font-weight:800;color:var(--muted);white-space:nowrap}
.operation{display:block;font-weight:400;color:var(--muted);font-size:.76rem;margin-top:2px}
.recovery{margin:11px 0;padding:9px 11px;border:1px solid var(--border);border-radius:10px;font-size:.8rem;font-weight:700}
.note{font-size:.72rem;color:var(--muted);text-align:center;margin:7px 0 0}
.empty{color:var(--muted);padding:12px 0}
@media(max-width:420px){main{padding:10px}.card{padding:15px}.metrics{gap:6px}.metric{padding:9px}.metric b{font-size:1.08rem}}
</style>
</head>
<body>
<main>
<section class="card" aria-live="polite" aria-label="Ripple repair plan and execution proof">
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

  const money = (value) => {
    const n = Number(value);
    return Number.isFinite(n) ? `$${Math.round(n).toLocaleString("en-US")}` : "";
  };

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

  const renderProposal = (card, root) => {
    const metrics = Array.isArray(card.metrics) ? card.metrics.slice(0, 3) : [];
    const impacts = Array.isArray(card.top_impacts) ? card.top_impacts : [];
    const scope = card.scope || {};
    const remaining = Number(card.remaining_impacts || 0);
    const decision = card.decision || {};
    const policy = card.selection_policy || {};
    const evidence = Array.isArray(card.optimization_evidence) ? card.optimization_evidence : [];
    const specific = evidence[0];

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
      ${policy.summary ? `<div class="why"><b>${esc(policy.label || "Why this plan?")}</b>${esc(policy.summary)}${specific ? `<span class="specific">${esc(specific.commitment)}: ${money(specific.net_advantage)} more net value than the next visible safe alternative.</span>` : ""}</div>` : ""}
      <div class="voice">${esc(card.voice_summary || "")}</div>
      <div class="decision" role="note" aria-label="${esc(card.accessibility_label || decision.label || "Approval required")}">${esc(decision.label || "Approval required")}</div>
      <p class="note">No changes occur until Alexa receives explicit approval for this exact plan.</p>
    `;
  };

  const renderExecution = (timeline, root) => {
    const counts = timeline.counts || {};
    const entries = Array.isArray(timeline.entries) ? timeline.entries : [];
    root.innerHTML = `
      <h1>${esc(timeline.headline || "Execution proof")}</h1>
      <p class="sub">${esc(timeline.subheadline || "")}</p>
      <p class="proof">${esc(timeline.proof_summary || "")}</p>
      <div class="metrics">
        <div class="metric"><b>${esc(counts.receipts || 0)}</b><span>Receipts</span></div>
        <div class="metric"><b>${esc(counts.executed_this_call || 0)}</b><span>New writes</span></div>
        <div class="metric"><b>${esc(counts.deduplicated_this_call || 0)}</b><span>Deduplicated</span></div>
      </div>
      ${timeline.recovered_after_restart ? `<div class="recovery">Restart recovered the same exact approved snapshot before execution resumed.</div>` : ""}
      <div class="receipts" aria-label="Execution receipts">
        ${entries.map(item => `<div class="receipt"><span class="label">${esc(item.label)}<span class="operation">${esc(item.operation)} · ${esc(item.provider)}</span></span><span class="status">${esc(item.status)}</span></div>`).join("")}
      </div>
      <div class="scope">${esc(counts.authoritative_unique_writes || 0)} authoritative provider writes total</div>
      <div class="why"><b>Safety receipt</b>${esc(timeline.safety_note || "")}</div>
    `;
  };

  const render = (payload) => {
    const root = document.getElementById("content");
    if (payload && payload.receipt_timeline && typeof payload.receipt_timeline === "object") {
      renderExecution(payload.receipt_timeline, root);
      notifySize();
      return;
    }
    const card = payload && payload.repair_card;
    if (card && typeof card === "object") {
      renderProposal(card, root);
      notifySize();
      return;
    }
    root.innerHTML = '<div class="empty">No repair proposal or execution proof to display yet.</div>';
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
        "description": "Money-first Alexa+ decision surface plus post-execution receipt proof for an exact Ripple repair plan.",
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
