"""Authenticated conditional provider API and client.

The server models a digital twin. It is never presented as a physical home.
Scenario events are injected through the separate SQLite fixture adapter, not
through model-accessible HTTP endpoints.
"""
from __future__ import annotations

import argparse
import hmac
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from .provider import ProviderRejected, SqliteWorld


def provider_app(world, token):
    if len(token) < 32: raise ValueError("Independent provider credential must be at least 32 characters")
    async def endpoint(request: Request):
        if not hmac.compare_digest(request.headers.get("authorization", ""), f"Bearer {token}"):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        try:
            if request.method == "GET":
                key = request.query_params.get("key")
                return JSONResponse({"receipt": world.lookup(key)} if key else world.read())
            raw = await request.body()
            if len(raw) > 24000: return JSONResponse({"error": "Request too large"}, status_code=413)
            args = json.loads(raw)
            if set(args) != {"action", "key", "expected_revision", "not_after"}: raise ValueError("Unexpected provider fields")
            return JSONResponse(world.apply(**args))
        except ProviderRejected as exc:
            return JSONResponse({"error": str(exc)}, status_code=409)
        except (ValueError, TypeError, KeyError) as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)
    return Starlette(routes=[Route("/world", endpoint, methods=["GET", "POST"])])


class HttpWorld:
    def __init__(self, base_url, token, *, client=None):
        url = urlsplit(base_url)
        if url.username or url.password or url.query or url.fragment or url.path not in {"", "/"}:
            raise ValueError("Provider URL must be a fixed origin")
        if url.scheme != "https" and not (url.scheme == "http" and url.hostname in {"localhost", "127.0.0.1"}):
            raise ValueError("HTTPS required outside loopback")
        if not token or len(token) < 32: raise ValueError("Independent provider credential required")
        self.url, self.token = base_url.rstrip("/"), token
        self.client = client or httpx.Client(timeout=5, follow_redirects=False, trust_env=False)

    def _call(self, method, **kwargs):
        response = self.client.request(method, self.url + "/world", headers={"Authorization": f"Bearer {self.token}"}, **kwargs)
        if response.status_code == 409: raise ProviderRejected(response.json()["error"])
        response.raise_for_status()
        if len(response.content) > 32000: raise ValueError("Provider response exceeds bounded schema")
        return response.json()

    def read(self): return self._call("GET")
    def lookup(self, key): return self._call("GET", params={"key": key})["receipt"]
    def apply(self, action, key, expected_revision, not_after):
        return self._call("POST", json={"action": action, "key": key, "expected_revision": expected_revision, "not_after": not_after})


def main():
    parser = argparse.ArgumentParser(description="Ripple conditional digital-twin provider")
    parser.add_argument("--database", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--clock-file", help="Offline evidence only: trusted integer scenario clock")
    args = parser.parse_args()
    clock = (lambda: int(Path(args.clock_file).read_text())) if args.clock_file else None
    world = SqliteWorld(args.database, source=args.source, clock=clock)
    import uvicorn
    uvicorn.run(provider_app(world, os.environ["RIPPLE_PROMISE_PROVIDER_TOKEN"]), host="127.0.0.1", port=args.port, log_level="error")


if __name__ == "__main__": main()
