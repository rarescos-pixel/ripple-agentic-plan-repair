from __future__ import annotations

import base64
import hashlib
import struct
from functools import lru_cache
from pathlib import Path

CAROUSEL_WIDTH = 600
CAROUSEL_HEIGHT = 900
CAROUSEL_SHA256 = "1cb7213204d308f63a910ba7599c4627cc9b9b381fcefbd8b527b2a4a57ba796"
_PARTS = 4


def _png_size(data: bytes) -> tuple[int, int]:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise RuntimeError("Alexa carousel payload is not a PNG")
    return struct.unpack(">II", data[16:24])


@lru_cache(maxsize=1)
def load_carousel_png() -> bytes:
    asset_dir = Path(__file__).with_name("assets")
    encoded = "".join(
        (asset_dir / f"carousel.b64.{index}").read_text(encoding="ascii").strip()
        for index in range(_PARTS)
    )
    data = base64.b64decode(encoded, validate=True)
    if _png_size(data) != (CAROUSEL_WIDTH, CAROUSEL_HEIGHT):
        raise RuntimeError("Alexa carousel dimensions drifted")
    if hashlib.sha256(data).hexdigest() != CAROUSEL_SHA256:
        raise RuntimeError("Alexa carousel payload checksum drifted")
    return data
