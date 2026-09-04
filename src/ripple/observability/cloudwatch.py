from __future__ import annotations

from dataclasses import dataclass
import json
import time
from typing import Any, Mapping, Protocol


class CloudWatchLogsClient(Protocol):
    def put_log_events(self, **kwargs): ...


SENSITIVE_KEYS = {
    "authorization", "password", "secret", "client_secret", "access_token",
    "refresh_token", "token", "cookie", "set-cookie", "api_key", "apikey",
}


def _redact(value: Any, *, key: str | None = None) -> Any:
    if key and key.lower().replace("-", "_") in {k.replace("-", "_") for k in SENSITIVE_KEYS}:
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return {str(k): _redact(v, key=str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(v) for v in value]
    if isinstance(value, tuple):
        return [_redact(v) for v in value]
    return value


@dataclass
class CloudWatchTraceSink:
    """Emit small structured trace events to a pre-created CloudWatch Logs stream.

    CloudWatch Logs no longer requires sequence-token chaining for PutLogEvents,
    so the runtime can safely emit independent small events without maintaining
    mutable sequence-token state.
    """

    client: CloudWatchLogsClient
    log_group: str
    log_stream: str
    max_message_bytes: int = 24_000

    def emit(
        self,
        event_type: str,
        *,
        correlation_id: str,
        payload: Mapping[str, Any] | None = None,
        timestamp_ms: int | None = None,
    ) -> dict[str, Any]:
        if not event_type or not correlation_id:
            raise ValueError("event_type and correlation_id are required")
        safe_payload = _redact(dict(payload or {}))
        envelope = {
            "schema": "ripple.trace.v1",
            "event_type": event_type,
            "correlation_id": correlation_id,
            "payload": safe_payload,
        }
        message = json.dumps(envelope, sort_keys=True, separators=(",", ":"), default=str)
        if len(message.encode("utf-8")) > self.max_message_bytes:
            raise ValueError("trace event exceeds configured message size")
        ts = int(timestamp_ms if timestamp_ms is not None else time.time() * 1000)
        self.client.put_log_events(
            logGroupName=self.log_group,
            logStreamName=self.log_stream,
            logEvents=[{"timestamp": ts, "message": message}],
        )
        return envelope
