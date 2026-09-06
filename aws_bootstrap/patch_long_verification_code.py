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

# Runtime imports needed to reconstruct AWS's displayed verification envelope.
if 'import base64\n' not in s:
    s = s.replace('import json\n', 'import base64\nimport json\n', 1)

old_validator = '''    code = str(data.get("code", "")).strip()\n    if not (4 <= len(code) <= 128) or not re.fullmatch(r"[A-Za-z0-9._-]+", code):\n        return JSONResponse({"ok": False, "error": "Invalid authorization-code format."}, status_code=400)'''
new_validator = '''    raw_code = str(data.get("code", ""))\n    # AWS's confirmation page displays a Base64 verification envelope whose\n    # decoded value is `code=<oauth-code>&state=<oauth-state>`. The browser\n    # controller intentionally returns only the short-lived `code` query value,\n    # so reconstruct the envelope here using this login process's own state.\n    code = re.sub(r"\\s+", "", raw_code)\n    is_envelope = False\n    try:\n        decoded = base64.b64decode(code, validate=True).decode("ascii")\n        is_envelope = decoded.startswith("code=") and "&state=" in decoded\n    except Exception:\n        is_envelope = False\n    if not is_envelope:\n        with lock:\n            current_auth_url = str(state.get("auth_url") or "")\n        m = re.search(r"[?&]state=([^&]+)", current_auth_url)\n        if not m:\n            return JSONResponse({"ok": False, "error": "AWS login state unavailable."}, status_code=409)\n        envelope = f"code={code}&state={m.group(1)}"\n        code = base64.b64encode(envelope.encode("ascii")).decode("ascii")\n    if not (16 <= len(code) <= 16384) or any(ord(ch) < 33 or ord(ch) > 126 for ch in code):\n        return JSONResponse({"ok": False, "error": "Invalid AWS verification-code format."}, status_code=400)'''
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

# Cost objective is zero. Add only the Cost Explorer permissions needed to read
# current spend and tighten the existing anomaly subscription; no broad billing/IAM access.
cost_anchor = '''            {\n                "Sid": "IdentityCheck",'''
cost_stmt = '''            {\n                "Sid": "RippleCostGuard",\n                "Effect": "Allow",\n                "Action": [\n                    "ce:GetCostAndUsage",\n                    "ce:GetAnomalySubscriptions",\n                    "ce:UpdateAnomalySubscription"\n                ],\n                "Resource": "*",\n            },\n'''
if '"Sid": "RippleCostGuard"' not in s:
    if cost_anchor not in s:
        raise SystemExit('IdentityCheck anchor not found for Cost Explorer permissions')
    s = s.replace(cost_anchor, cost_stmt + cost_anchor, 1)

path.write_text(s, encoding='utf-8')
print('patched AWS bootstrap for immutable OIDC subject, verification envelope, sanitized diagnostics, and least-privilege cost guard access')
