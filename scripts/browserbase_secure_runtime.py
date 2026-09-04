from __future__ import annotations

import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

BASE = "https://api.browserbase.com/v1"
REQUEST_PATH = pathlib.Path("automation/browser-secure-request.json")
RESULT_PATH = pathlib.Path("/tmp/browser-secure-result.json")
CERT_PATH = pathlib.Path("/tmp/browser-secure-recipient.crt")


def fail(message: str, code: int = 1) -> None:
    print(message)
    raise SystemExit(code)


def request_json(method: str, path: str, api_key: str, body: object | None = None) -> tuple[int, object]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={
            "X-BB-API-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8", "replace")
            status = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        status = exc.code
    try:
        parsed: object = json.loads(raw) if raw else None
    except json.JSONDecodeError:
        parsed = {"raw": raw[:4000]}
    return status, parsed


def main() -> None:
    api_key = os.getenv("BROWSERBASE_API_KEY", "").strip()
    if not api_key:
        fail("BROWSERBASE_API_KEY_UNAVAILABLE", 2)

    request = json.loads(REQUEST_PATH.read_text("utf-8"))
    op = str(request.get("op", "")).strip()
    cert = str(request.get("recipientCertPem", "")).strip()
    if not cert.startswith("-----BEGIN CERTIFICATE-----"):
        fail("recipient certificate missing", 3)

    if op == "build_status":
        build_id = str(request.get("buildId", "")).strip()
        if not build_id:
            fail("buildId missing", 4)
        status, body = request_json("GET", f"/functions/builds/{build_id}", api_key)
    elif op == "invocation_status":
        invocation_id = str(request.get("invocationId", "")).strip()
        if not invocation_id:
            fail("invocationId missing", 4)
        status, body = request_json("GET", f"/functions/invocations/{invocation_id}", api_key)
    elif op == "invoke":
        function_id = str(request.get("functionId", "")).strip()
        params = request.get("params")
        if not function_id or not isinstance(params, dict):
            fail("functionId/params missing", 4)
        status, body = request_json("POST", f"/functions/{function_id}/invoke", api_key, {"params": params})
    else:
        fail("unsupported operation", 4)

    envelope = {
        "operation": op,
        "httpStatus": status,
        "body": body,
    }
    RESULT_PATH.write_text(json.dumps(envelope, ensure_ascii=False), "utf-8")
    CERT_PATH.write_text(cert + "\n", "utf-8")
    print(f"browserbase_operation_complete op={op} http_status={status}")


if __name__ == "__main__":
    main()
