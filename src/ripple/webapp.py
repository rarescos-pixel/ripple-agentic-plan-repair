from __future__ import annotations

import json
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict

from ripple.evaluation.matrix import run_matrix
from ripple.golden import build_golden
from ripple.orchestration.agent import GoldenChangeInterpreter, RippleAgent
from ripple.orchestration.session import RippleSession
from ripple.domain.models import Approval
from ripple.presentation import build_repair_card


GOLDEN_CONTEXT = {"old_arrival_at": "2026-09-10T21:00:00"}


class DemoController:
    """Stateful local Alexa+ simulation controller.

    The controller deliberately exposes a two-phase contract: proposal first,
    execution only after an explicit approve call for the current proposal.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> Dict[str, Any]:
        _, tools, planner, executor, _ = build_golden()
        self.tools = tools
        self.agent = RippleAgent(GoldenChangeInterpreter(), planner)
        self.session = RippleSession(self.agent, executor)
        self.proposal = None
        self.last_receipts = []
        self.last_approval = None
        return {"status": "reset"}

    def propose(self, utterance: str) -> Dict[str, Any]:
        self.proposal = self.session.propose(utterance, GOLDEN_CONTEXT)
        self.last_receipts = []
        plan = self.proposal.plan
        repair_card = build_repair_card(plan)
        return {
            "phase": "proposal",
            "spoken_summary": self.proposal.spoken_summary,
            "repair_card": repair_card,
            "requires_approval": self.proposal.requires_approval,
            "plan": {
                "id": plan.id,
                "version": plan.version,
                "snapshot_hash": plan.snapshot_hash(),
                "impact_count": len(plan.impacts),
                "action_count": len(plan.actions),
                "total_added_cost": plan.total_added_cost,
                "total_avoidable_loss": plan.total_avoidable_loss,
                "net_direct_cash_preserved": plan.net_direct_cash_preserved,
                "external_people_notified": plan.external_people_notified,
                "unresolved_items": list(plan.unresolved_items),
                "impacts": [
                    {
                        "affected_node_id": i.affected_node_id,
                        "dependency_path": list(i.dependency_path),
                        "reason": i.reason,
                        "status": i.status.value,
                        "direct_cash_at_risk": i.direct_cash_at_risk,
                        "urgency": i.urgency,
                    }
                    for i in plan.impacts
                ],
                "actions": [
                    {
                        "id": a.id,
                        "tool": a.tool,
                        "operation": a.operation,
                        "target_id": a.target_id,
                        "params": a.params,
                        "added_cost": a.added_cost,
                        "avoidable_loss": a.avoidable_loss,
                        "reversible": a.reversible,
                        "idempotency_key": a.idempotency_key,
                    }
                    for a in plan.actions
                ],
            },
            "approval_disclosure": {
                "plan_id": plan.id,
                "plan_version": plan.version,
                "snapshot_hash": plan.snapshot_hash(),
                "max_total_cost": plan.total_added_cost,
                "external_people_notified": plan.external_people_notified,
                "irreversible_actions": [a.id for a in plan.actions if not a.reversible],
                "external_services": sorted({a.tool for a in plan.actions}),
            },
            "writes_before_approval": len(self.tools.execution_log),
        }

    def evidence(self) -> Dict[str, Any]:
        rows = run_matrix()
        return {
            "passed": sum(1 for r in rows if r.passed),
            "total": len(rows),
            "scenarios": [asdict(r) for r in rows],
        }

    def approve(self, disclosure: Dict[str, Any]) -> Dict[str, Any]:
        if self.proposal is None:
            raise ValueError("No active proposal to approve")
        required = {
            "plan_id",
            "plan_version",
            "snapshot_hash",
            "max_total_cost",
            "external_people_notified",
        }
        if not required.issubset(disclosure):
            raise ValueError("Approval must echo the exact client-visible disclosure")
        approval = Approval(
            plan_id=str(disclosure["plan_id"]),
            plan_version=int(disclosure["plan_version"]),
            max_total_cost=float(disclosure["max_total_cost"]),
            external_people_notified=int(disclosure["external_people_notified"]),
            plan_snapshot_hash=str(disclosure["snapshot_hash"]),
            actor="user",
        )
        result = self.session.execute_with_approval(self.proposal, approval)
        self.last_approval = approval
        self.last_receipts = result.receipts
        plan = self.proposal.plan
        return {
            "phase": "executed",
            "plan_status": plan.status,
            "receipt_count": len(result.receipts),
            "receipts": [asdict(r) for r in result.receipts],
            "external_write_count": len(self.tools.execution_log),
        }

    def replay(self) -> Dict[str, Any]:
        if self.proposal is None:
            raise ValueError("No active proposal to replay")
        if self.last_approval is None:
            raise ValueError("No accepted approval to replay")
        result = self.session.execute_with_approval(self.proposal, self.last_approval)
        return {
            "phase": "replay",
            "receipt_count": len(result.receipts),
            "deduplicated": sum(1 for r in result.receipts if r.status == "deduplicated"),
            "external_write_count": len(self.tools.execution_log),
            "receipts": [asdict(r) for r in result.receipts],
        }


INDEX_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ripple — Alexa+ simulation</title>
<style>
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#151821;background:#f3f5f8}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(180deg,#eef1f6 0,#f7f8fa 320px)}
main{max-width:1080px;margin:0 auto;padding:36px 20px 72px}.hero{padding:16px 2px 22px}
.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-size:.74rem;font-weight:800;color:#60697a}
h1{font-size:3rem;letter-spacing:-.055em;margin:4px 0 5px}h2{letter-spacing:-.025em}.sub{font-size:1.12rem;max-width:700px;color:#596273;margin:0}
.card{background:#fff;border:1px solid #dfe3ea;border-radius:18px;padding:22px;margin:14px 0;box-shadow:0 8px 30px #1b243008}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:14px}.wide{grid-column:span 8}.side{grid-column:span 4}
textarea{width:100%;min-height:92px;resize:vertical;font:inherit;padding:14px;border-radius:12px;border:1px solid #cbd1dc;background:#fbfcfe}
button{font:inherit;padding:11px 16px;border-radius:11px;border:1px solid #bbc2ce;cursor:pointer;margin:8px 8px 0 0;background:#fff}
.primary{background:#171a22;color:#fff;border-color:#171a22;font-weight:750}.metric-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:16px 0}
.metric{padding:14px;border:1px solid #e0e4ea;border-radius:13px;background:#fafbfc}.metric b{display:block;font-size:1.65rem;letter-spacing:-.035em}.metric span{font-size:.82rem;color:#687083}
.money-line{font-weight:850;font-size:1.08rem;margin:10px 0 2px}.badge{display:inline-flex;align-items:center;border:1px solid #d8dde5;border-radius:999px;padding:5px 9px;font-size:.78rem;font-weight:700;margin:2px 5px 2px 0;background:#fbfcfd}
.proof{font-weight:800}.ok{color:#17643b}.warn{color:#84520d}.muted{color:#697286}.hidden{display:none}.impact{border-left:3px solid #9ca5b4;padding:6px 0 6px 12px;margin:10px 0}
.voice{background:#f8f9fb;border-radius:13px;padding:13px 14px;margin:14px 0;color:#333a47}.action{padding:11px 0;border-bottom:1px solid #edf0f4}.action:last-child{border-bottom:0}
.op,.hash{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}.op{font-weight:700}.money{font-variant-numeric:tabular-nums}
.disclosure{background:#f8f9fb;border:1px solid #e0e4eb;border-radius:13px;padding:14px;margin-top:16px}.hash{font-size:.76rem;word-break:break-all;color:#626b7c}
details{margin-top:14px;border-top:1px solid #edf0f4;padding-top:12px}summary{cursor:pointer;font-weight:750;color:#4f5868}
table{width:100%;border-collapse:collapse;font-size:.9rem}th,td{text-align:left;padding:9px;border-bottom:1px solid #e8ebef;vertical-align:top}th{font-size:.76rem;text-transform:uppercase;letter-spacing:.06em;color:#697286}
.scenario{padding:10px 0;border-bottom:1px solid #edf0f4}.scenario:last-child{border-bottom:0}
@media(max-width:760px){h1{font-size:2.35rem}.wide,.side{grid-column:span 12}.metric-grid{grid-template-columns:1fr}}
</style>
</head>
<body><main>
<section class="hero"><div class="eyebrow">Amazon Developer Hackathon · simulated Alexa+ experience</div><h1>Ripple</h1><p class="sub">Tell Alexa one thing that changed. Ripple finds what breaks downstream, quantifies what is at risk, and asks for one exact approval before bounded repairs execute.</p></section>
<div class="grid">
<section class="card wide"><label><b>Simulated Alexa+ request</b></label><textarea id="utterance">Our flight home was cancelled. We'll land tomorrow at 18:00.</textarea><button class="primary" onclick="propose()">Ask Ripple</button><button onclick="resetDemo()">Reset</button></section>
<aside class="card side"><b>Trust boundary</b><p class="muted">LLM proposes → deterministic policy validates → exact plan approval → bounded idempotent writes → receipts.</p><div id="evidenceSummary" class="badge">Loading validation…</div></aside>
</div>
<section id="proposal" class="card hidden"></section>
<section id="execution" class="card hidden"></section>
<section id="evidence" class="card"><h2>Executable safety evidence</h2><p class="muted">Adversarial scenarios executed by the evaluation harness, not marketing claims.</p><div id="evidenceRows">Loading…</div></section>
</main>
<script>
let currentApproval=null;
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function post(path,body={}){const r=await fetch(path,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});const j=await r.json();if(!r.ok)throw new Error(j.error||'request failed');return j}
async function get(path){const r=await fetch(path);const j=await r.json();if(!r.ok)throw new Error(j.error||'request failed');return j}
function money(v){return '$'+Number(v).toFixed(0)}
function technicalEvidence(p,d){return `<details><summary>Technical evidence</summary><h3>Bounded repair actions</h3>${p.actions.map(a=>`<div class="action"><span class="op">${esc(a.tool)}.${esc(a.operation)}</span> → <b>${esc(a.target_id)}</b><br><span class="muted">+${money(a.added_cost)} · avoids ${money(a.avoidable_loss)} · ${a.reversible?'reversible':'irreversible'} · idem ${esc(a.idempotency_key.slice(0,10))}…</span></div>`).join('')}<div class="disclosure"><b>Exact approval snapshot</b><p>${d.external_services.length} services · max cost ${money(d.max_total_cost)} · ${d.external_people_notified} people notified · ${d.irreversible_actions.length} irreversible action(s)</p><div class="hash">snapshot ${esc(d.snapshot_hash)}</div></div></details>`}
async function propose(){
  try{
    const j=await post('/api/propose',{utterance:document.getElementById('utterance').value});
    const p=j.plan,d=j.approval_disclosure,c=j.repair_card;
    currentApproval=d;
    document.getElementById('proposal').classList.remove('hidden');
    document.getElementById('execution').classList.add('hidden');
    const impacts=c.top_impacts.map(i=>`<div class="impact"><b>${esc(i.label)}</b>${Number(i.cash_at_risk.replace(/[$,]/g,''))>0?` · <span class="money">${esc(i.cash_at_risk)} at risk</span>`:''}</div>`).join('');
    const more=c.remaining_impacts?`<div class="muted">+${c.remaining_impacts} more affected commitment${c.remaining_impacts===1?'':'s'}</div>`:'';
    const metrics=c.metrics.map(m=>`<div class="metric"><b class="money">${esc(m.value)}</b><span>${esc(m.label)}</span></div>`).join('');
    const scope=`${c.scope.actions} actions · ${c.scope.services} services${c.scope.people_notified?` · ${c.scope.people_notified} people notified`:''}`;
    document.getElementById('proposal').innerHTML=`<div class="eyebrow">Phase 1 · proposal only</div><h2>${esc(c.headline)}</h2><div class="money-line">${esc(c.money_summary)}</div><div class="metric-grid">${metrics}</div><div class="voice" aria-label="${esc(c.accessibility_label)}">“${esc(c.voice_summary)}”</div><h3>Top consequences</h3>${impacts}${more}<p class="muted">${esc(scope)}</p><p class="proof ok">✓ External writes before approval: ${j.writes_before_approval}</p><button class="primary" aria-label="${esc(c.decision.voice_prompt)}" onclick="approve()">${esc(c.decision.label)}</button>${technicalEvidence(p,d)}`;
  }catch(e){alert(e.message)}
}
function receiptTable(rs){return `<table><thead><tr><th>Action</th><th>Status</th><th>Result</th></tr></thead><tbody>${rs.map(r=>`<tr><td>${esc(r.action_id)}</td><td><b>${esc(r.status)}</b></td><td>${esc(r.result.operation||'')} → ${esc(r.result.target_id||'')}</td></tr>`).join('')}</tbody></table>`}
async function approve(){try{if(!currentApproval)throw new Error('No captured approval snapshot');const j=await post('/api/approve',currentApproval);document.getElementById('execution').classList.remove('hidden');document.getElementById('execution').innerHTML=`<div class="eyebrow">Phase 2 · bounded execution</div><h2>Authoritative receipts</h2><p class="proof ok">✓ Plan status: ${esc(j.plan_status)} · unique external writes: ${j.external_write_count}</p>${receiptTable(j.receipts)}<button onclick="replay()">Replay exact approved plan</button><div id="replayProof"></div>`}catch(e){alert(e.message)}}
async function replay(){try{const j=await post('/api/replay');document.getElementById('replayProof').innerHTML=`<div class="disclosure proof ok">✓ Replay safety: ${j.deduplicated}/${j.receipt_count} actions deduplicated. Unique external write count remains ${j.external_write_count}.</div>`}catch(e){alert(e.message)}}
async function resetDemo(){await post('/api/reset');currentApproval=null;document.getElementById('proposal').classList.add('hidden');document.getElementById('execution').classList.add('hidden')}
async function loadEvidence(){try{const j=await get('/api/evidence');document.getElementById('evidenceSummary').textContent=`${j.passed}/${j.total} adversarial scenarios PASS`;document.getElementById('evidenceRows').innerHTML=j.scenarios.map(s=>`<div class="scenario"><span class="badge ${s.passed?'ok':'warn'}">${s.passed?'PASS':'FAIL'}</span><b>${esc(s.scenario)}</b><div class="muted">${esc(s.invariant)}</div></div>`).join('')}catch(e){document.getElementById('evidenceRows').textContent=e.message}}
loadEvidence();
</script>
</body></html>'''


class RippleHandler(BaseHTTPRequestHandler):
    controller = DemoController()

    def _json(self, status: int, payload: Dict[str, Any]) -> None:
        raw = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        if self.path == "/api/evidence":
            self._json(200, self.controller.evidence())
            return
        if self.path != "/":
            self.send_error(404)
            return
        raw = INDEX_HTML.encode()
        self.send_response(200)
        self.send_header("content-type", "text/html; charset=utf-8")
        self.send_header("content-length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("content-length", "0"))
            body = json.loads(self.rfile.read(length) or b"{}")
            if self.path == "/api/propose":
                payload = self.controller.propose(str(body.get("utterance", "")))
            elif self.path == "/api/approve":
                payload = self.controller.approve(body)
            elif self.path == "/api/replay":
                payload = self.controller.replay()
            elif self.path == "/api/reset":
                payload = self.controller.reset()
            else:
                self._json(404, {"error": "not_found"})
                return
            self._json(200, payload)
        except Exception as exc:
            self._json(400, {"error": str(exc)})

    def log_message(self, format: str, *args: Any) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = ThreadingHTTPServer((host, port), RippleHandler)
    print(f"Ripple demo: http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    serve()
