#!/usr/bin/env python3
"""Exercise real browser review controls against the local continuous worker.

Uses an isolated digital twin and ephemeral human credential. Requires Playwright
and Chromium/Chrome. Never touches the published AWS runtime or a real device.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time


def port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--screenshot", default=None)
    args = parser.parse_args()
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory(prefix="ripple-review-test-") as temporary:
        root = Path(temporary)
        app_port, provider_port = port(), port()
        while app_port == provider_port: provider_port = port()
        log_file = root / "server.log"
        with log_file.open("w") as log:
            process = subprocess.Popen([sys.executable, "scripts/promise_local_demo.py", "--port", str(app_port),
                "--provider-port", str(provider_port), "--data-dir", str(root / "state")], stdout=log, stderr=subprocess.STDOUT)
            try:
                token = None
                for _ in range(200):
                    content = log_file.read_text()
                    match = re.search(r"Private review code: (.+)", content)
                    if match:
                        token = match.group(1)
                        break
                    if process.poll() is not None: raise RuntimeError("Isolated demo process failed to start")
                    time.sleep(.05)
                if token is None: raise RuntimeError("Demo readiness deadline exceeded")
                base = f"http://127.0.0.1:{app_port}"
                with sync_playwright() as playwright:
                    executable = os.getenv("RIPPLE_BROWSER_EXECUTABLE") or shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
                    browser = playwright.chromium.launch(headless=True, executable_path=executable)
                    try:
                        page = browser.new_page(viewport={"width": 1440, "height": 1080})
                        errors = []
                        page.on("pageerror", lambda error: errors.append(str(error)))
                        page.goto(base + "/promises/review/hero")
                        page.locator("#code").fill(token)
                        page.locator("#open").click()
                        page.locator("#content:not(.hidden)").wait_for()
                        assert "DRAFT" in page.locator("#status").inner_text()
                        page.locator("#confirm").click()
                        page.wait_for_function("!document.querySelector('#approve').disabled")
                        page.locator("#approve").click()

                        def event(name):
                            response = page.request.post(base + "/demo/event", headers={"Authorization": "Bearer " + token}, data={"event": name})
                            assert response.ok, response.text()
                            return response.json()

                        event("guest_leaves")
                        page.locator("#refresh").click()
                        page.wait_for_function("!document.querySelector('#approve').disabled")
                        page.locator("#approve").click()
                        page.wait_for_function("document.querySelector('#latest').textContent.includes('independently verified')")
                        event("departure_delayed")
                        page.locator("#refresh").click()
                        page.wait_for_function("!document.querySelector('#approve').disabled")
                        if args.screenshot:
                            Path(args.screenshot).parent.mkdir(parents=True, exist_ok=True)
                            page.screenshot(path=args.screenshot, full_page=True)
                        page.locator("#approve").click()
                        old = event("old_departure")
                        assert old["world"]["facts"]["common_mode"] == "home"
                        held = event("new_departure")
                        assert held["state"]["decision"] == "WAIT_FOR_EVIDENCE"
                        event("family_departs")
                        page.locator("#refresh").click()
                        page.wait_for_function("!document.querySelector('#approve').disabled")
                        page.locator("#approve").click()
                        page.wait_for_function("document.querySelector('#metrics strong').textContent === '2'")
                        completed = event("completion")
                        assert completed["state"]["phase"] == "SATISFIED" and completed["writes"] == 2
                        page.locator("#refresh").click()
                        page.wait_for_function("document.querySelector('#status').textContent.includes('SATISFIED')")
                        assert errors == [], errors
                        print("PROMISE_BROWSER_GATE=PASS; meaning/action separation, two verified effects, stale-world repair, terminal read-back")
                    finally:
                        browser.close()
            finally:
                process.terminate()
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


if __name__ == "__main__": main()
