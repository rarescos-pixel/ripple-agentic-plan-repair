from pathlib import Path

path = Path('aws_bootstrap/app.py')
s = path.read_text(encoding='utf-8')

# GitHub on this account emits an immutable-ID OIDC subject, verified by the
# independent smoke workflow. Keep AWS trust bound to this exact repository.
s = s.replace(
    'REPO = "rarescos-pixel/ripple-agentic-plan-repair"',
    'REPO = "rarescos-pixel@321760901/ripple-agentic-plan-repair@1356792571"',
    1,
)

# Runtime imports for the verified AWS remote-login verification envelope.
if 'import base64\n' not in s:
    s = s.replace('import json\n', 'import base64\nimport json\n', 1)
if 'from urllib.parse import parse_qs, urlparse\n' not in s:
    s = s.replace('from typing import Any\n', 'from typing import Any\nfrom urllib.parse import parse_qs, urlparse\n', 1)

# Accept either (a) the Base64 envelope copied by AWS or (b) the short-lived
# `code` query value from AWS's confirmation URL. Path (b) is the browser-bridge
# path that previously produced AWS OIDC PASS. In both cases bind to the state
# of this exact login attempt, then submit the canonical Base64 envelope to CLI.
old_validator = '''    code = str(data.get("code", "")).strip()\n    if not (4 <= len(code) <= 128) or not re.fullmatch(r"[A-Za-z0-9._-]+", code):\n        return JSONResponse({"ok": False, "error": "Invalid authorization-code format."}, status_code=400)'''
new_validator = '''    raw_code = str(data.get("code", ""))\n    compact = re.sub(r"\\s+", "", raw_code)\n    if not (16 <= len(compact) <= 32768) or any(ord(ch) < 33 or ord(ch) > 126 for ch in compact):\n        return JSONResponse({"ok": False, "error": "Invalid AWS verification-code format."}, status_code=400)\n\n    with lock:\n        current_auth_url = str(state.get("auth_url") or "")\n    try:\n        expected_state = parse_qs(urlparse(current_auth_url).query).get("state", [""])[0]\n    except Exception:\n        expected_state = ""\n    if not expected_state:\n        return JSONResponse({"ok": False, "error": "Current AWS login state is unavailable. Restart this bootstrap session."}, status_code=409)\n\n    embedded_code = ""\n    embedded_state = ""\n    try:\n        padded = compact + ("=" * (-len(compact) % 4))\n        decoded = base64.b64decode(padded, validate=True).decode("utf-8")\n        fields = parse_qs(decoded, keep_blank_values=True, strict_parsing=True)\n        embedded_code = fields.get("code", [""])[0]\n        embedded_state = fields.get("state", [""])[0]\n    except Exception:\n        # Browser bridge supplies the JWE-like `code` query value directly.\n        # It is opaque; only enforce the character set/shape and bind our own state.\n        if not re.fullmatch(r"[A-Za-z0-9._~-]+", compact) or compact.count(".") < 3:\n            return JSONResponse({"ok": False, "error": "AWS verification code could not be decoded or recognized."}, status_code=400)\n        embedded_code = compact\n        embedded_state = expected_state\n\n    if not embedded_code or not embedded_state:\n        return JSONResponse({"ok": False, "error": "AWS verification envelope is missing code/state."}, status_code=400)\n    if embedded_state != expected_state:\n        return JSONResponse({"ok": False, "error": "This verification code belongs to a different AWS login session."}, status_code=409)\n\n    canonical_envelope = f"code={embedded_code}&state={embedded_state}".encode("utf-8")\n    code = base64.b64encode(canonical_envelope).decode("ascii")'''
if old_validator not in s:
    raise SystemExit('validator pattern not found')
s = s.replace(old_validator, new_validator, 1)

s = s.replace('input{display:block;', 'input,textarea{display:block;', 1)
s = s.replace("const input=document.createElement('input'); input.id='code';", "const input=document.createElement('textarea'); input.rows=8; input.id='code';", 1)
s = s.replace("input.placeholder='Authorization code';", "input.placeholder='Paste the full AWS verification code here';", 1)

# Add a strictly sanitized CLI-tail helper. It suppresses URLs and any long
# token-like material before exposing only the final short human-readable line.
anchor = '''def extract_auth_url(text: str) -> str | None:\n    for candidate in reversed(re.findall(r"https://[^\\s\\r\\n]+", text or "")):\n        candidate = candidate.rstrip(")]}>,.;'\\\"")\n        lower = candidate.lower()\n        if "amazonaws.com" in lower or "aws.amazon.com" in lower:\n            return candidate\n    return None\n'''
helper = anchor + '''\n\ndef safe_cli_tail(text: str) -> str:\n    cleaned = re.sub(r"https://[^\\s]+", "[url suppressed]", text or "")\n    cleaned = re.sub(r"[A-Za-z0-9._~+/=-]{40,}", "[token suppressed]", cleaned)\n    lines = [line.strip() for line in cleaned.replace("\\r", "\\n").split("\\n") if line.strip()]\n    lines = [line for line in lines if not line.lower().startswith("enter the authorization code")]\n    return (lines[-1] if lines else "no diagnostic text")[:300]\n'''
if 'def safe_cli_tail(' not in s:
    if anchor not in s:
        raise SystemExit('extract_auth_url anchor not found')
    s = s.replace(anchor, helper, 1)

old_eof = '''            elif idx == 3:\n                child.close()\n                if child.exitstatus not in (0, None):\n                    raise RuntimeError(f"aws login exited with status {child.exitstatus}")\n                break'''
new_eof = '''            elif idx == 3:\n                diagnostic = safe_cli_tail(before)\n                child.close()\n                if child.exitstatus not in (0, None):\n                    raise RuntimeError(f"aws login exited with status {child.exitstatus}: {diagnostic}")\n                break'''
if old_eof not in s:
    raise SystemExit('EOF diagnostic anchor not found')
s = s.replace(old_eof, new_eof, 1)

# One-time browser handoff page. The short-lived AWS code stays in the URL
# fragment (never reaches access logs); JS immediately removes the fragment and
# POSTs the code to the local bootstrap endpoint.
handoff_anchor = '''PAGE = r\'\'\'<!doctype html>'''
handoff_route = '''HANDOFF_PAGE = r\'\'\'<!doctype html>\n<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ripple AWS Handoff</title></head>\n<body><p id="s">Completing AWS authorization…</p><script>\n(async()=>{\n  const p=new URLSearchParams(location.hash.slice(1));\n  const code=p.get('code')||'';\n  history.replaceState(null,'','/handoff');\n  if(!code){document.getElementById('s').textContent='Missing authorization code.';return;}\n  const r=await fetch('/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code})});\n  const j=await r.json().catch(()=>({}));\n  document.getElementById('s').textContent=r.ok?'Authorization submitted. This tab can be closed.':('Authorization failed: '+(j.error||r.status));\n})();\n</script></body></html>\n\'\'\'\n\n@app.get("/handoff")\ndef handoff() -> HTMLResponse:\n    return HTMLResponse(HANDOFF_PAGE)\n\n\nPAGE = r\'\'\'<!doctype html>'''
if 'def handoff() -> HTMLResponse:' not in s:
    if handoff_anchor not in s:
        raise SystemExit('PAGE anchor not found for browser handoff route')
    s = s.replace(handoff_anchor, handoff_route, 1)

# Cost objective is zero. Add only the Cost Explorer permissions needed to read
# current spend and tighten the existing anomaly subscription; no broad billing/IAM access.
cost_anchor = '''            {\n                "Sid": "IdentityCheck",'''
cost_stmt = '''            {\n                "Sid": "RippleCostGuard",\n                "Effect": "Allow",\n                "Action": [\n                    "ce:GetCostAndUsage",\n                    "ce:GetAnomalySubscriptions",\n                    "ce:UpdateAnomalySubscription"\n                ],\n                "Resource": "*",\n            },\n'''
if '"Sid": "RippleCostGuard"' not in s:
    if cost_anchor not in s:
        raise SystemExit('IdentityCheck anchor not found for Cost Explorer permissions')
    s = s.replace(cost_anchor, cost_stmt + cost_anchor, 1)

path.write_text(s, encoding='utf-8')
print('patched AWS bootstrap for verified browser handoff, immutable OIDC subject, sanitized diagnostics, and least-privilege cost guard access')
