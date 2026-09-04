from __future__ import annotations

import json
import struct
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "addon-package" / "addon.json"
REQUIRED_ICON_SIZES = {(64, 64), (72, 72), (88, 88), (126, 126), (180, 180), (241, 241)}
PROD_MCP = "https://ripple-v12-production.up.railway.app/mcp"


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise AssertionError(f"Not a valid PNG header: {path}")
    return struct.unpack(">II", data[16:24])


def assert_https(value: str) -> None:
    parsed = urlparse(value)
    assert parsed.scheme == "https" and parsed.netloc, value


def local_asset_from_uri(uri: str) -> Path:
    prefix = "https://raw.githubusercontent.com/rarescos-pixel/ripple-agentic-plan-repair/main/"
    assert uri.startswith(prefix), uri
    return ROOT / uri.removeprefix(prefix)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["manifestVersion"] == "1.0"
    assert manifest.get("accountLinking", {}).get("enabled") is True

    listing = manifest["storeListing"]
    assert listing["distributionCountries"] == ["US"]
    locale = listing["locales"]["en-US"]

    name = locale["name"]["value"]
    short = locale["shortDescription"]
    full = locale["fullDescription"]
    phrases = locale["examplePhrases"]
    assert 1 <= len(name) <= 30
    assert 1 <= len(short) <= 123
    assert 1 <= len(full) <= 4000
    assert 3 <= len(phrases) <= 4
    assert len(set(phrases)) == len(phrases)
    assert all(1 <= len(p) <= 200 for p in phrases)

    privacy = locale["privacyAndCompliance"]
    assert_https(privacy["privacyPolicyUrl"])
    assert_https(privacy["termsOfUseUrl"])

    media = locale["mediaAssets"]
    icons = media["icons"]["light"]
    declared = set()
    for icon in icons:
        assert_https(icon["uri"])
        size = tuple(map(int, icon["size"].split("x")))
        declared.add(size)
        path = local_asset_from_uri(icon["uri"])
        assert path.exists(), path
        assert png_size(path) == size, (path, png_size(path), size)
    assert declared == REQUIRED_ICON_SIZES

    carousel = media["carouselImages"]
    assert carousel
    for image in carousel:
        assert_https(image["uri"])
        assert 1 <= len(image["altText"]) <= 250
        size = tuple(map(int, image["size"].split("x")))
        assert size == (600, 900)
        path = local_asset_from_uri(image["uri"])
        assert path.exists(), path
        assert png_size(path) == size

    integrations = manifest["integrations"]
    assert len(integrations) == 1 and integrations[0]["type"] == "MCP"
    endpoint = integrations[0]["config"]["endpoints"]["default"]
    assert endpoint["type"] == "HTTPS"
    assert endpoint["uri"] == PROD_MCP
    assert_https(endpoint["uri"])

    print("Ripple Alexa+ add-on package gate: PASS")
    print("name:", name)
    print("icons:", len(icons), "required sizes")
    print("carousel:", len(carousel), "600x900")
    print("account linking: enabled")
    print("mcp:", endpoint["uri"])


if __name__ == "__main__":
    main()
