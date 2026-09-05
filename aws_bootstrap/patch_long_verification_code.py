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

path.write_text(s, encoding='utf-8')
print('patched AWS bootstrap for long verification codes')
