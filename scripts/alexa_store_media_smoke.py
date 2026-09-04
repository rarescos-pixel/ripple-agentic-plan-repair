"""Remote evidence gate for Alexa+ store assets and public listing URLs."""
from __future__ import annotations

import json
import os
import struct
from pathlib import Path

import httpx

from ripple.presentation.alexa_assets import CAROUSEL_SHA256

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "addon-package" / "addon.json"
BASE_URL = os.getenv("RIPPLE_SMOKE_BASE_URL", "https://ripple-v12-production.up.railway.app").rstrip("/")
REQUIRED_ICON_SIZES = {(64, 64), (72, 72), (88, 88), (126, 126), (180, 180), (241, 241)}


def png_size(data: bytes) -> tuple[int, int]:
    assert len(data) >= 24
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert data[12:16] == b"IHDR"
    return struct.unpack(">II", data[16:24])


def fetch_ok(client: httpx.Client, url: str) -> httpx.Response:
    response = client.get(url)
    response.raise_for_status()
    return response


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    locale = manifest["storeListing"]["locales"]["en-US"]
    media = locale["mediaAssets"]
    endpoint = manifest["integrations"][0]["config"]["endpoints"]["default"]["uri"]
    assert endpoint == f"{BASE_URL}/mcp"

    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        carousel = media["carouselImages"][0]
        carousel_response = fetch_ok(client, carousel["uri"])
        assert carousel_response.headers.get("content-type", "").startswith("image/png")
        assert png_size(carousel_response.content) == (600, 900)
        import hashlib

        assert hashlib.sha256(carousel_response.content).hexdigest() == CAROUSEL_SHA256
        cache_control = carousel_response.headers.get("cache-control", "")
        assert "immutable" in cache_control
        assert carousel_response.headers.get("x-content-type-options") == "nosniff"

        privacy = locale["privacyAndCompliance"]
        privacy_response = fetch_ok(client, privacy["privacyPolicyUrl"])
        terms_response = fetch_ok(client, privacy["termsOfUseUrl"])
        assert "Ripple Privacy Policy" in privacy_response.text
        assert "Ripple Terms" in terms_response.text

        declared_sizes = set()
        for icon in media["icons"]["light"]:
            response = fetch_ok(client, icon["uri"])
            assert response.headers.get("content-type", "").startswith("image/png")
            actual = png_size(response.content)
            declared = tuple(map(int, icon["size"].split("x")))
            assert actual == declared
            declared_sizes.add(actual)
        assert declared_sizes == REQUIRED_ICON_SIZES

    print("Ripple Alexa store-media remote gate: PASS")
    print("mcp:", endpoint)
    print("carousel: 600x900 / exact sha256 / immutable / nosniff")
    print("privacy_terms: reachable and non-placeholder")
    print("icons: 6/6 exact dimensions")


if __name__ == "__main__":
    main()
