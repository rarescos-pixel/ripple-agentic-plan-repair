from __future__ import annotations

import json
import os

from starlette.requests import Request
from starlette.routing import Route

from app import app, _no_store_json

VERIFY_STATUS_FILE = os.getenv("AWS_VERIFY_STATUS_FILE", "/data/aws_verify.json").strip() or "/data/aws_verify.json"
_ALLOWED = {
    "ok",
    "signedIn",
    "cloudShellReached",
    "hostClass",
    "pathClass",
    "httpStatus",
    "verifiedAt",
    "errorType",
}


async def verify_status(_: Request):
    payload = None
    try:
        if os.path.exists(VERIFY_STATUS_FILE):
            with open(VERIFY_STATUS_FILE, "r", encoding="utf-8") as handle:
                raw = json.load(handle)
            if isinstance(raw, dict):
                payload = {key: raw.get(key) for key in _ALLOWED if key in raw}
    except Exception:
        payload = {"ok": False, "errorType": "StatusReadError"}
    return _no_store_json({"ok": True, "awsAuthVerify": payload})


app.router.routes.append(Route("/verify-status", verify_status, methods=["GET"]))
