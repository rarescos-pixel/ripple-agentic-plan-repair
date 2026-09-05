from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from urllib.parse import urlparse

from playwright.async_api import async_playwright

PROFILE_DIR = os.getenv("BROWSER_PROFILE_DIR", "/data/chromium-profile").strip() or "/data/chromium-profile"
TARGET = "https://console.aws.amazon.com/cloudshell/home?region=eu-central-1"
STATUS_FILE = os.getenv("AWS_VERIFY_STATUS_FILE", "/data/aws_verify.json").strip() or "/data/aws_verify.json"


def classify_url(url: str) -> dict[str, object]:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    path = parsed.path or "/"
    is_signin = host == "signin.aws.amazon.com" or host.endswith(".signin.aws.amazon.com")
    is_console = host == "console.aws.amazon.com" or host.endswith(".console.aws.amazon.com")
    is_cloudshell = is_console and path.startswith("/cloudshell")
    return {
        "signedIn": bool(is_console and not is_signin),
        "cloudShellReached": bool(is_cloudshell),
        "hostClass": "signin" if is_signin else ("console" if is_console else "other"),
        "pathClass": "cloudshell" if is_cloudshell else "other",
    }


async def main() -> None:
    outcome: dict[str, object] = {
        "ok": False,
        "signedIn": False,
        "cloudShellReached": False,
        "hostClass": "unknown",
        "pathClass": "unknown",
        "httpStatus": None,
    }

    context = None
    try:
        os.makedirs(PROFILE_DIR, exist_ok=True)
        async with async_playwright() as playwright:
            context = await playwright.chromium.launch_persistent_context(
                PROFILE_DIR,
                headless=True,
                viewport={"width": 1440, "height": 900},
                args=[
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-background-networking",
                ],
            )
            pages = context.pages
            page = pages[0] if pages else await context.new_page()
            response = await page.goto(TARGET, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)
            outcome.update(classify_url(page.url))
            outcome["httpStatus"] = response.status if response else None
            outcome["ok"] = True
            await context.close()
            context = None
    except Exception as exc:
        outcome["errorType"] = type(exc).__name__
    finally:
        if context is not None:
            try:
                await context.close()
            except Exception:
                pass

    outcome["verifiedAt"] = datetime.now(timezone.utc).isoformat()
    public = {
        key: outcome.get(key)
        for key in (
            "ok", "signedIn", "cloudShellReached", "hostClass",
            "pathClass", "httpStatus", "verifiedAt", "errorType"
        )
        if key in outcome
    }
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as handle:
            json.dump(public, handle, sort_keys=True)
    except Exception:
        pass
    print("AWS_AUTH_VERIFY " + json.dumps(public, sort_keys=True), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
