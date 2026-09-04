from __future__ import annotations

import asyncio
import json
import os
from typing import Any
from urllib.parse import urlparse

import httpx
from playwright.async_api import async_playwright
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

UPSTREAM_BROKER_URL = os.getenv("BROWSERBASE_BROKER_URL", "").strip()
BROKER_TOKEN = os.getenv("BROKER_TOKEN", "").strip()
ALLOWED_HOST_SUFFIXES = tuple(
    x.strip().lower()
    for x in os.getenv(
        "ALLOWED_HOST_SUFFIXES",
        "example.com,amazon.com,aws.amazon.com",
    ).split(",")
    if x.strip()
)


def _no_store(payload: object, status_code: int = 200) -> JSONResponse:
    response = JSONResponse(payload, status_code=status_code)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response


def _authorized(request: Request) -> bool:
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth[7:].strip()
    return bool(BROKER_TOKEN) and token == BROKER_TOKEN


def _host_allowed(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.hostname or "").lower()
    return bool(host) and any(host == suffix or host.endswith("." + suffix) for suffix in ALLOWED_HOST_SUFFIXES)


def _timeout_ms(value: Any, default: int = 30000) -> int:
    try:
        raw = int(value)
    except (TypeError, ValueError):
        raw = default
    return max(1, min(raw, 120000))


async def _mint_session() -> str:
    if not UPSTREAM_BROKER_URL:
        raise RuntimeError("BROWSERBASE_BROKER_URL is not configured")
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.get(UPSTREAM_BROKER_URL)
    if response.status_code >= 400:
        raise RuntimeError(f"upstream broker returned HTTP {response.status_code}")
    try:
        body = response.json()
    except Exception as exc:
        raise RuntimeError("upstream broker returned non-JSON") from exc
    connect_url = body.get("connectUrl") if isinstance(body, dict) else None
    if not isinstance(connect_url, str) or not connect_url:
        raise RuntimeError("upstream broker response is missing connectUrl")
    return connect_url


async def health(_: Request) -> JSONResponse:
    return _no_store(
        {
            "ok": True,
            "upstreamConfigured": bool(UPSTREAM_BROKER_URL),
            "brokerTokenConfigured": bool(BROKER_TOKEN),
            "allowedHostCount": len(ALLOWED_HOST_SUFFIXES),
        }
    )


async def upstream_test(request: Request) -> JSONResponse:
    if not _authorized(request):
        return _no_store({"error": "unauthorized"}, 401)
    try:
        connect_url = await _mint_session()
        return _no_store({"ok": True, "connectUrlPresent": bool(connect_url)})
    except Exception as exc:
        return _no_store({"ok": False, "error": str(exc)[:500]}, 502)


async def run_browser(request: Request) -> JSONResponse:
    if not _authorized(request):
        return _no_store({"error": "unauthorized"}, 401)

    try:
        payload = await request.json()
    except Exception:
        return _no_store({"error": "invalid_json"}, 400)

    if not isinstance(payload, dict):
        return _no_store({"error": "body_must_be_object"}, 400)

    target = str(payload.get("url") or "").strip()
    if not target or not _host_allowed(target):
        return _no_store({"error": "target_not_allowed"}, 403)

    steps = payload.get("steps") or []
    if not isinstance(steps, list) or len(steps) > 40:
        return _no_store({"error": "invalid_steps"}, 400)

    sensitive = payload.get("sensitive", True) is not False
    allow_sensitive_output = payload.get("allowSensitiveOutput", False) is True
    can_return_observed = (not sensitive) or allow_sensitive_output
    wait_until = str(payload.get("waitUntil") or "domcontentloaded")
    if wait_until not in {"load", "domcontentloaded", "networkidle", "commit"}:
        wait_until = "domcontentloaded"
    request_timeout = _timeout_ms(payload.get("timeoutMs"), 30000)

    result: dict[str, Any] = {
        "ok": False,
        "sensitive": sensitive,
        "stepCount": len(steps),
        "steps": [],
    }

    browser = None
    try:
        connect_url = await _mint_session()
        async with async_playwright() as playwright:
            browser = await playwright.chromium.connect_over_cdp(connect_url, timeout=request_timeout)
            contexts = browser.contexts
            if not contexts:
                raise RuntimeError("remote browser has no context")
            context = contexts[0]
            pages = context.pages
            page = pages[0] if pages else await context.new_page()

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
                    if not step_url or not _host_allowed(step_url):
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
                    ms = max(0, min(int(step.get("ms") or 0), 10000))
                    await page.wait_for_timeout(ms)
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
            await browser.close()
            browser = None
            return _no_store(result)
    except Exception as exc:
        result["error"] = str(exc)[:1000]
        return _no_store(result, 502)
    finally:
        if browser is not None:
            try:
                await browser.close()
            except Exception:
                pass


app = Starlette(
    routes=[
        Route("/healthz", health, methods=["GET"]),
        Route("/upstream-test", upstream_test, methods=["GET"]),
        Route("/run", run_browser, methods=["POST"]),
    ]
)
