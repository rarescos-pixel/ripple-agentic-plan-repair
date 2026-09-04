from __future__ import annotations

import asyncio
import hmac
import ipaddress
import json
import os
import socket
from typing import Any
from urllib.parse import urlparse

from playwright.async_api import BrowserContext, Frame, Locator, Page, Playwright, async_playwright
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Route

BROKER_TOKEN = os.getenv("BROKER_TOKEN", "").strip()
LIVE_TOKEN = os.getenv("LIVE_TOKEN", "").strip()
PROFILE_DIR = os.getenv("BROWSER_PROFILE_DIR", "/data/chromium-profile").strip() or "/data/chromium-profile"
VIEWPORT_WIDTH = 1440
VIEWPORT_HEIGHT = 900

PLAYWRIGHT: Playwright | None = None
CONTEXT: BrowserContext | None = None
PAGE: Page | None = None
BROWSER_ERROR: str | None = None
BROWSER_LOCK = asyncio.Lock()


def _no_store_json(payload: object, status_code: int = 200) -> JSONResponse:
    response = JSONResponse(payload, status_code=status_code)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response


def _no_store_response(content: bytes, media_type: str) -> Response:
    response = Response(content, media_type=media_type)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


def _bearer_authorized(request: Request) -> bool:
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth[7:].strip()
    return bool(BROKER_TOKEN) and hmac.compare_digest(token, BROKER_TOKEN)


def _live_authorized(token: str) -> bool:
    return bool(LIVE_TOKEN) and hmac.compare_digest(token, LIVE_TOKEN)


def _timeout_ms(value: Any, default: int = 30000) -> int:
    try:
        raw = int(value)
    except (TypeError, ValueError):
        raw = default
    return max(1, min(raw, 120000))


def _ip_is_public(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return True
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _resolve_host(host: str) -> list[str]:
    infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    return sorted({str(info[4][0]) for info in infos})


async def _url_allowed(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host or host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        return False
    if not _ip_is_public(host):
        return False
    try:
        addresses = await asyncio.wait_for(asyncio.to_thread(_resolve_host, host), timeout=5)
    except Exception:
        return False
    return bool(addresses) and all(_ip_is_public(address) for address in addresses)


async def _ensure_page() -> Page:
    global PAGE
    if CONTEXT is None:
        raise RuntimeError(BROWSER_ERROR or "browser context is not ready")
    if PAGE is None or PAGE.is_closed():
        pages = CONTEXT.pages
        PAGE = pages[0] if pages else await CONTEXT.new_page()
    return PAGE


async def browser_startup() -> None:
    global PLAYWRIGHT, CONTEXT, PAGE, BROWSER_ERROR
    try:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        PLAYWRIGHT = await async_playwright().start()
        CONTEXT = await PLAYWRIGHT.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=True,
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-background-networking",
            ],
        )
        pages = CONTEXT.pages
        PAGE = pages[0] if pages else await CONTEXT.new_page()
        BROWSER_ERROR = None
        print("LOCAL_BROWSER_READY", flush=True)
    except Exception as exc:
        BROWSER_ERROR = str(exc)[:1000]
        print("LOCAL_BROWSER_ERROR " + json.dumps({"error": BROWSER_ERROR}), flush=True)


async def browser_shutdown() -> None:
    global PLAYWRIGHT, CONTEXT, PAGE
    try:
        if CONTEXT is not None:
            await CONTEXT.close()
    finally:
        CONTEXT = None
        PAGE = None
        if PLAYWRIGHT is not None:
            await PLAYWRIGHT.stop()
        PLAYWRIGHT = None


async def health(_: Request) -> JSONResponse:
    ready = CONTEXT is not None and BROWSER_ERROR is None
    return _no_store_json(
        {
            "ok": True,
            "browserReady": ready,
            "profilePersistenceConfigured": PROFILE_DIR.startswith("/data/"),
            "brokerTokenConfigured": bool(BROKER_TOKEN),
            "liveHandoffConfigured": bool(LIVE_TOKEN),
            "viewport": [VIEWPORT_WIDTH, VIEWPORT_HEIGHT],
            "browserError": None if ready else BROWSER_ERROR,
        }
    )


async def browser_meta(request: Request) -> JSONResponse:
    if not _bearer_authorized(request):
        return _no_store_json({"error": "unauthorized"}, 401)
    try:
        async with BROWSER_LOCK:
            page = await _ensure_page()
            return _no_store_json({"ok": True, "url": page.url, "title": await page.title()})
    except Exception as exc:
        return _no_store_json({"ok": False, "error": str(exc)[:500]}, 503)


async def run_browser(request: Request) -> JSONResponse:
    if not _bearer_authorized(request):
        return _no_store_json({"error": "unauthorized"}, 401)
    try:
        payload = await request.json()
    except Exception:
        return _no_store_json({"error": "invalid_json"}, 400)
    if not isinstance(payload, dict):
        return _no_store_json({"error": "body_must_be_object"}, 400)

    target = str(payload.get("url") or "").strip()
    if not target or not await _url_allowed(target):
        return _no_store_json({"error": "target_not_allowed"}, 403)
    steps = payload.get("steps") or []
    if not isinstance(steps, list) or len(steps) > 40:
        return _no_store_json({"error": "invalid_steps"}, 400)

    sensitive = payload.get("sensitive", True) is not False
    allow_sensitive_output = payload.get("allowSensitiveOutput", False) is True
    can_return_observed = (not sensitive) or allow_sensitive_output
    wait_until = str(payload.get("waitUntil") or "domcontentloaded")
    if wait_until not in {"load", "domcontentloaded", "networkidle", "commit"}:
        wait_until = "domcontentloaded"
    request_timeout = _timeout_ms(payload.get("timeoutMs"), 30000)
    result: dict[str, Any] = {"ok": False, "sensitive": sensitive, "stepCount": len(steps), "steps": []}

    try:
        async with BROWSER_LOCK:
            page = await _ensure_page()
            navigation = await page.goto(target, wait_until=wait_until, timeout=request_timeout)
            result["initialHttpStatus"] = navigation.status if navigation else None

            for index, step in enumerate(steps, start=1):
                if not isinstance(step, dict):
                    raise RuntimeError(f"step {index}: must be an object")
                action = str(step.get("action") or "")
                if not action:
                    raise RuntimeError(f"step {index}: action is required")
                timeout = _timeout_ms(step.get("timeoutMs"), request_timeout)
                item: dict[str, Any] = {"index": index, "action": action, "ok": False}

                if action == "goto":
                    step_url = str(step.get("url") or "").strip()
                    if not step_url or not await _url_allowed(step_url):
                        raise RuntimeError(f"step {index}: target not allowed")
                    await page.goto(step_url, wait_until="domcontentloaded", timeout=timeout)
                elif action == "waitForSelector":
                    selector = str(step.get("selector") or "")
                    if not selector:
                        raise RuntimeError(f"step {index}: selector is required")
                    state = str(step.get("state") or "visible")
                    if state not in {"attached", "detached", "visible", "hidden"}:
                        state = "visible"
                    await page.locator(selector).wait_for(state=state, timeout=timeout)
                elif action == "waitForTimeout":
                    await page.wait_for_timeout(max(0, min(int(step.get("ms") or 0), 10000)))
                elif action == "assertText":
                    selector = str(step.get("selector") or "")
                    if not selector:
                        raise RuntimeError(f"step {index}: selector is required")
                    text = (await page.locator(selector).text_content(timeout=timeout)) or ""
                    if "equals" in step and text.strip() != str(step.get("equals")):
                        raise RuntimeError(f"step {index}: text equality assertion failed")
                    if "contains" in step and str(step.get("contains")) not in text:
                        raise RuntimeError(f"step {index}: text contains assertion failed")
                    if can_return_observed:
                        item["observedText"] = text.strip()[:1000]
                elif action == "assertTitle":
                    title = await page.title()
                    if "equals" in step and title != str(step.get("equals")):
                        raise RuntimeError(f"step {index}: title equality assertion failed")
                    if "contains" in step and str(step.get("contains")) not in title:
                        raise RuntimeError(f"step {index}: title contains assertion failed")
                    if can_return_observed:
                        item["observedTitle"] = title
                elif action == "assertUrl":
                    current = page.url
                    if "equals" in step and current != str(step.get("equals")):
                        raise RuntimeError(f"step {index}: URL equality assertion failed")
                    if "contains" in step and str(step.get("contains")) not in current:
                        raise RuntimeError(f"step {index}: URL contains assertion failed")
                    if can_return_observed:
                        item["observedUrl"] = current
                elif action == "readText":
                    selector = str(step.get("selector") or "")
                    if not selector:
                        raise RuntimeError(f"step {index}: selector is required")
                    text = (await page.locator(selector).text_content(timeout=timeout)) or ""
                    item["observed"] = text.strip()[:4000] if can_return_observed else "suppressed"
                elif action == "readAttribute":
                    selector = str(step.get("selector") or "")
                    attribute = str(step.get("attribute") or "")
                    if not selector or not attribute:
                        raise RuntimeError(f"step {index}: selector and attribute are required")
                    value = await page.locator(selector).get_attribute(attribute, timeout=timeout)
                    item["observed"] = value if can_return_observed else "suppressed"
                else:
                    raise RuntimeError(f"step {index}: unsupported read-only action {action}")

                item["ok"] = True
                result["steps"].append(item)

            result["ok"] = True
            if can_return_observed:
                result["finalUrl"] = page.url
                result["title"] = await page.title()
            return _no_store_json(result)
    except Exception as exc:
        result["error"] = str(exc)[:1000]
        return _no_store_json(result, 502)


async def _frame_focus(frame: Frame) -> dict[str, Any] | None:
    try:
        info = await frame.evaluate(
            """() => {
                const e = document.activeElement;
                if (!e) return null;
                const tag = (e.tagName || '').toLowerCase();
                const type = (e.getAttribute && e.getAttribute('type') || '').toLowerCase();
                const editable = tag === 'textarea' || e.isContentEditable ||
                  (tag === 'input' && !['button','submit','reset','checkbox','radio','file','hidden','image','range','color'].includes(type));
                return {editable, tag, type, id: e.id || '', name: (e.getAttribute && e.getAttribute('name')) || ''};
            }"""
        )
        if isinstance(info, dict):
            return info
    except Exception:
        pass
    return None


async def _focused_editable(page: Page) -> dict[str, Any] | None:
    for frame in page.frames:
        info = await _frame_focus(frame)
        if info and info.get("editable"):
            return info
    return None


async def _first_editable(page: Page, kind: str) -> tuple[Locator, str] | None:
    if kind == "secret":
        selectors = [
            'input[type="password"]',
            'input[autocomplete="current-password"]',
            'input[autocomplete="new-password"]',
            'input[type="text"]',
            'input:not([type])',
            'textarea',
        ]
    else:
        selectors = [
            'input[type="email"]',
            'input[autocomplete="username"]',
            'input[type="text"]',
            'input:not([type])',
            'input[type="tel"]',
            'input[inputmode="numeric"]',
            'input[type="number"]',
            'textarea',
        ]

    for frame in page.frames:
        for selector in selectors:
            try:
                locator = frame.locator(selector)
                count = min(await locator.count(), 20)
                for idx in range(count):
                    candidate = locator.nth(idx)
                    if await candidate.is_visible() and await candidate.is_enabled():
                        return candidate, selector
            except Exception:
                continue
    return None


async def _type_smart(page: Page, text: str, kind: str) -> dict[str, Any]:
    focused = await _focused_editable(page)
    if focused:
        # keyboard.type emits the key/input event sequence that many login forms expect.
        await page.keyboard.type(text, delay=25)
        return {"mode": "focused", "target": f"{focused.get('tag','')}:{focused.get('type','')}"}

    found = await _first_editable(page, kind)
    if found is None:
        raise RuntimeError("no editable field is focused or visible")

    candidate, selector = found
    await candidate.click(timeout=10000)
    try:
        await candidate.fill(text, timeout=10000)
        mode = "smart-fill"
    except Exception:
        await page.keyboard.type(text, delay=25)
        mode = "smart-type"
    return {"mode": mode, "target": selector}


LIVE_HTML = """<!doctype html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Private Browser Login</title>
<style>
body{font-family:system-ui,sans-serif;margin:0;background:#111;color:#eee}#bar{position:sticky;top:0;z-index:2;background:#1c1c1c;padding:10px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}input,button{font-size:16px;padding:9px;border-radius:8px;border:1px solid #555;background:#222;color:#fff}#url{min-width:280px;flex:1}.entry{min-width:220px;flex:0 1 320px}.muted{font-size:12px;color:#aaa;max-width:720px}#frame{display:block;width:100%;height:auto;cursor:crosshair;background:#fff}#status{font-size:12px;min-width:160px;font-weight:600}</style>
</head><body><div id='bar'>
<input id='url' placeholder='https://...'><button onclick='nav()'>Go</button><button onclick="act({action:'reload'})">Reload</button>
<input id='textbox' class='entry' type='text' autocomplete='off' autocapitalize='none' spellcheck='false' placeholder='Email / username / MFA code'><button onclick="sendBox('textbox','text')">Send text</button>
<input id='secretbox' class='entry' type='password' autocomplete='off' placeholder='Password / secret'><button onclick="sendBox('secretbox','secret')">Send secret</button>
<button onclick="key('Tab')">Tab</button><button onclick="key('Enter')">Enter</button><button onclick="key('Backspace')">Backspace</button><button onclick='clearRemote()'>Clear field</button>
<span id='status'>connecting…</span><span class='muted'>Click the remote field if you want. Send text also auto-finds the first visible editable field when focus is missing. Secret text goes directly to this Railway browser service, not through ChatGPT.</span>
</div><img id='frame' alt='browser view'>
<script>
const token=location.pathname.split('/')[2]; const base='/live/'+token; const img=document.getElementById('frame'); const status=document.getElementById('status');
async function act(body){status.textContent='working…';try{let r=await fetch(base+'/action',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});let j=await r.json();if(j.ok){status.textContent='ok'+(j.inputMode?' – '+j.inputMode:'')+(j.focused===true?' – field focused':'');}else{status.textContent=j.error||'error';}if(j.url)document.getElementById('url').value=j.url;}catch(e){status.textContent='network error';}refresh();}
function nav(){let u=document.getElementById('url').value.trim();if(u)act({action:'navigate',url:u});}
function sendBox(id,kind){let el=document.getElementById(id);let text=el.value;el.value='';if(text)act({action:'type',text,kind});}
function key(k){act({action:'press',key:k});}
function clearRemote(){act({action:'clearFocused'});}
img.addEventListener('click',e=>{let r=img.getBoundingClientRect();let x=(e.clientX-r.left)*(img.naturalWidth/r.width);let y=(e.clientY-r.top)*(img.naturalHeight/r.height);act({action:'click',x,y});});
function refresh(){img.src=base+'/screenshot?t='+Date.now();fetch(base+'/meta').then(r=>r.json()).then(j=>{if(j.url)document.getElementById('url').value=j.url;}).catch(()=>{});}
img.onload=()=>{if(status.textContent==='connecting…')status.textContent='ready';};setInterval(refresh,1200);refresh();
</script></body></html>"""


async def live_page(request: Request) -> Response:
    if not _live_authorized(request.path_params["token"]):
        return Response("Not found", status_code=404)
    response = HTMLResponse(LIVE_HTML)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    return response


async def live_screenshot(request: Request) -> Response:
    if not _live_authorized(request.path_params["token"]):
        return Response("Not found", status_code=404)
    try:
        async with BROWSER_LOCK:
            page = await _ensure_page()
            data = await page.screenshot(type="png", full_page=False)
        return _no_store_response(data, "image/png")
    except Exception as exc:
        return _no_store_json({"ok": False, "error": str(exc)[:300]}, 503)


async def live_meta(request: Request) -> JSONResponse:
    if not _live_authorized(request.path_params["token"]):
        return _no_store_json({"error": "not_found"}, 404)
    try:
        async with BROWSER_LOCK:
            page = await _ensure_page()
            focus = await _focused_editable(page)
            return _no_store_json({"ok": True, "url": page.url, "title": await page.title(), "editableFocused": bool(focus)})
    except Exception as exc:
        return _no_store_json({"ok": False, "error": str(exc)[:300]}, 503)


async def live_action(request: Request) -> JSONResponse:
    if not _live_authorized(request.path_params["token"]):
        return _no_store_json({"error": "not_found"}, 404)
    try:
        body = await request.json()
    except Exception:
        return _no_store_json({"error": "invalid_json"}, 400)
    if not isinstance(body, dict):
        return _no_store_json({"error": "invalid_body"}, 400)
    action = str(body.get("action") or "")
    try:
        async with BROWSER_LOCK:
            page = await _ensure_page()
            extra: dict[str, Any] = {}
            if action == "click":
                x = max(0.0, min(float(body.get("x", 0)), VIEWPORT_WIDTH))
                y = max(0.0, min(float(body.get("y", 0)), VIEWPORT_HEIGHT))
                await page.mouse.click(x, y)
                extra["focused"] = bool(await _focused_editable(page))
            elif action == "type":
                text = str(body.get("text") or "")[:4096]
                if not text:
                    return _no_store_json({"error": "empty_text"}, 400)
                kind = str(body.get("kind") or "text")
                if kind not in {"text", "secret"}:
                    kind = "text"
                typed = await _type_smart(page, text, kind)
                extra["inputMode"] = typed["mode"]
                extra["focused"] = True
            elif action == "press":
                key = str(body.get("key") or "")
                allowed = {"Enter", "Tab", "Escape", "Backspace", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "PageUp", "PageDown"}
                if key not in allowed:
                    return _no_store_json({"error": "key_not_allowed"}, 403)
                await page.keyboard.press(key)
            elif action == "clearFocused":
                if not await _focused_editable(page):
                    return _no_store_json({"error": "no_editable_field_focused"}, 409)
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Backspace")
            elif action == "navigate":
                target = str(body.get("url") or "").strip()
                if not target or not await _url_allowed(target):
                    return _no_store_json({"error": "target_not_allowed"}, 403)
                await page.goto(target, wait_until="domcontentloaded", timeout=60000)
            elif action == "reload":
                await page.reload(wait_until="domcontentloaded", timeout=60000)
            elif action == "scroll":
                dy = max(-5000, min(int(body.get("dy") or 0), 5000))
                await page.mouse.wheel(0, dy)
            else:
                return _no_store_json({"error": "action_not_allowed"}, 403)
            return _no_store_json({"ok": True, "url": page.url, **extra})
    except Exception as exc:
        return _no_store_json({"ok": False, "error": str(exc)[:500]}, 502)


app = Starlette(
    routes=[
        Route("/healthz", health, methods=["GET"]),
        Route("/meta", browser_meta, methods=["GET"]),
        Route("/run", run_browser, methods=["POST"]),
        Route("/live/{token}", live_page, methods=["GET"]),
        Route("/live/{token}/screenshot", live_screenshot, methods=["GET"]),
        Route("/live/{token}/meta", live_meta, methods=["GET"]),
        Route("/live/{token}/action", live_action, methods=["POST"]),
    ],
    on_startup=[browser_startup],
    on_shutdown=[browser_shutdown],
)
