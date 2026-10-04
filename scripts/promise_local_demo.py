#!/usr/bin/env python3
"""Local human review + continuous worker + separate conditional HTTP provider.

Everything affects a clearly labelled digital twin. The draft is the reviewed
fixture from examples.py; this runner does not pretend to call Alexa or Bedrock.
"""
from __future__ import annotations

import argparse
import asyncio
from contextlib import asynccontextmanager
import hmac
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.routing import Route

from ripple.promises.engine import PromiseEngine
from ripple.promises.examples import household
from ripple.promises.interface import PromiseService, human_routes
from ripple.promises.provider import SqliteWorld
from ripple.promises.provider_http import HttpWorld
from ripple.promises.store import SqlitePromiseStore


CONTROLS = """<!doctype html><html lang="en"><meta charset="utf-8"><title>Ripple · Scenario controls</title>
<style>body{font:17px/1.5 system-ui;max-width:700px;margin:60px auto;padding:20px;color:#183d31}button,input{font:inherit;padding:12px;margin:8px}button{background:#006e5b;color:white;border:0;border-radius:8px}pre{white-space:pre-wrap}</style>
<h1>Digital twin scenario controls</h1><p>This panel changes the demo world. It does not approve Ripple's actions.</p>
<p><a href="/promises/review/hero" target="_blank" rel="noopener">Open human review</a></p>
<input id="code" type="password" placeholder="Private review code" autocomplete="off">
<div><button data-event="guest_leaves">1 · Mom goes out</button><button data-event="departure_delayed">2 · Departure moves later</button><button data-event="old_departure">3 · Reach the old departure time</button><button data-event="new_departure">4 · Reach the new departure time</button><button data-event="family_departs">5 · Family departure observed</button><button data-event="completion">6 · Completion verified</button></div><pre id="out"></pre>
<script>for(const button of document.querySelectorAll("button")){button.onclick=async()=>{const r=await fetch("/demo/event",{method:"POST",headers:{Authorization:"Bearer "+document.getElementById("code").value,"Content-Type":"application/json"},body:JSON.stringify({event:button.dataset.event})});document.getElementById("out").textContent=JSON.stringify(await r.json(),null,2)}};</script></html>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--provider-port", type=int, default=8766)
    parser.add_argument("--data-dir", default=None, help="Fresh directory; existing databases are never reset")
    args = parser.parse_args()
    root = Path(args.data_dir or tempfile.mkdtemp(prefix="ripple-promise-demo-"))
    root.mkdir(parents=True, exist_ok=True)
    if (root / "world.db").exists(): raise SystemExit("Choose a fresh demo directory; refusing to overwrite existing world state")
    # Fixed, explicitly simulated time: Sep 27, 2026, 18:59 UTC.
    from datetime import datetime, timezone
    start = int(datetime(2026, 9, 27, 18, 59, tzinfo=timezone.utc).timestamp())
    clock_file = root / "clock"
    clock_file.write_text(str(start))
    clock = lambda: int(clock_file.read_text())
    contract, catalog, facts = household(start)
    fixture = SqliteWorld(root / "world.db", source="household-twin", clock=clock)
    fixture.seed(facts)
    provider_token, human_token = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    process = subprocess.Popen([sys.executable, "-m", "ripple.promises.provider_http", "--database", str(root / "world.db"),
        "--source", "household-twin", "--port", str(args.provider_port), "--clock-file", str(clock_file)],
        env=dict(os.environ, RIPPLE_PROMISE_PROVIDER_TOKEN=provider_token))
    remote = HttpWorld(f"http://127.0.0.1:{args.provider_port}", provider_token)
    try:
        for _ in range(100):
            try:
                remote.read()
                break
            except Exception:
                if process.poll() is not None: raise RuntimeError("Provider failed to start")
                time.sleep(.03)
        else: raise RuntimeError("Provider readiness deadline exceeded")
        engine = PromiseEngine(SqlitePromiseStore(root / "promises.db"), remote, catalog, clock=clock)
        engine.draft("hero", "local-human", contract)
        service = PromiseService(engine, None, "local-human", human_token)
        service.worker.register("hero")
        # Domain facts/events are fixture adapters. No engine branch knows these names.
        events = {"guest_leaves": (start + 10, {"guest_present": False}),
                  "departure_delayed": (start + 20, {"departure_at": start + 100}),
                  "old_departure": (start + 60, {}), "new_departure": (start + 100, {}),
                  "family_departs": (start + 100, {"family_departed": True}),
                  "completion": (start + 100, {"departure_verified": True})}
        async def home(request): return RedirectResponse("/promises/review/hero")
        async def controls(request): return HTMLResponse(CONTROLS, headers={"Cache-Control": "no-store"})
        async def event(request):
            if not hmac.compare_digest(request.headers.get("authorization", ""), "Bearer " + human_token):
                return JSONResponse({"error": "Private review code required"}, status_code=401)
            data = await request.json()
            if set(data) != {"event"} or data["event"] not in events:
                return JSONResponse({"error": "Unknown scenario event"}, status_code=400)
            at, patch = events[data["event"]]
            if at < clock(): return JSONResponse({"error": "Scenario time cannot rewind"}, status_code=409)
            clock_file.write_text(str(at))
            if patch: fixture.change(patch)
            await asyncio.to_thread(service.worker.tick)
            state = engine.get("hero", "local-human")
            return JSONResponse({"scope": "digital twin", "state": service.present(state), "world": remote.read(), "writes": fixture.write_count()})
        @asynccontextmanager
        async def lifespan(app):
            async def watch():
                while True:
                    await asyncio.to_thread(service.worker.tick)
                    await asyncio.sleep(1)
            task = asyncio.create_task(watch())
            try: yield
            finally:
                task.cancel()
                try: await task
                except asyncio.CancelledError: pass
        app = Starlette(lifespan=lifespan, routes=human_routes(lambda request: service) + [
            Route("/", home), Route("/demo", controls), Route("/demo/event", event, methods=["POST"])])
        print(f"Digital twin only. Intent normalization uses a reviewed fixture.\nReview: http://127.0.0.1:{args.port}/\nScenario controls: http://127.0.0.1:{args.port}/demo\nPrivate review code: {human_token}\nEvidence directory: {root}", flush=True)
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
    finally:
        process.terminate()
        try: process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__": main()
