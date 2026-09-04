from __future__ import annotations

import asyncio
import hashlib
import struct

import httpx

from ripple.asgi import CAROUSEL_PATH, app
from ripple.presentation.alexa_assets import (
    CAROUSEL_HEIGHT,
    CAROUSEL_SHA256,
    CAROUSEL_WIDTH,
    load_carousel_png,
)


def _run(coro):
    return asyncio.run(coro)


def _png_size(data: bytes) -> tuple[int, int]:
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert data[12:16] == b"IHDR"
    return struct.unpack(">II", data[16:24])


def test_carousel_payload_is_exact_and_stable():
    data = load_carousel_png()
    assert _png_size(data) == (CAROUSEL_WIDTH, CAROUSEL_HEIGHT) == (600, 900)
    assert hashlib.sha256(data).hexdigest() == CAROUSEL_SHA256


def test_production_asgi_wrapper_serves_carousel_without_breaking_mcp_app():
    async def case():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            asset = await client.get(CAROUSEL_PATH)
            assert asset.status_code == 200
            assert asset.headers["content-type"].startswith("image/png")
            assert asset.headers["cache-control"] == "public, max-age=86400, immutable"
            assert asset.headers["x-content-type-options"] == "nosniff"
            assert _png_size(asset.content) == (600, 900)
            assert hashlib.sha256(asset.content).hexdigest() == CAROUSEL_SHA256

            # The wrapper must be transparent for the existing application.
            health = await client.get("/healthz")
            assert health.status_code == 200
            assert health.json()["service"] == "ripple-plan-repair"
            assert health.json()["version"] == "1.5.0"

    _run(case())
