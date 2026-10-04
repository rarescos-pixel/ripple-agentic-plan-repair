"""Human review surface. Never exposes authority through a model-callable tool."""
import base64
import hashlib
from pathlib import Path
import re

from starlette.responses import HTMLResponse


async def review_page(request):
    html = Path(__file__).with_name("review.html").read_text()
    script = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
    style = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    def sha(text): return base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()
    csp = f"default-src 'none'; script-src 'sha256-{sha(script)}'; style-src 'sha256-{sha(style)}'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
    return HTMLResponse(html, headers={"Content-Security-Policy": csp, "Cache-Control": "no-store", "Referrer-Policy": "no-referrer", "X-Content-Type-Options": "nosniff"})
