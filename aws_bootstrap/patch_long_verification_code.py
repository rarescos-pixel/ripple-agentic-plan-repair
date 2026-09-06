from pathlib import Path

path = Path('aws_bootstrap/app.py')
s = path.read_text(encoding='utf-8')

old_validator = '''    code = str(data.get("code", "")).strip()\n    if not (4 <= len(code) <= 128) or not re.fullmatch(r"[A-Za-z0-9._-]+", code):\n        return JSONResponse({"ok": False, "error": "Invalid authorization-code format."}, status_code=400)'''
new_validator = '''    raw_code = str(data.get("code", ""))\n    # AWS remote login may return a long verification blob. Browser wrapping or\n    # copy/paste can insert whitespace, so normalize whitespace only.\n    code = re.sub(r"\\s+", "", raw_code)\n    if not (16 <= len(code) <= 16384) or any(ord(ch) < 33 or ord(ch) > 126 for ch in code):\n        return JSONResponse({"ok": False, "error": "Invalid AWS verification-code format."}, status_code=400)'''
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

path.write_text(s, encoding='utf-8')
print('patched AWS bootstrap for long verification codes and sanitized diagnostics')
