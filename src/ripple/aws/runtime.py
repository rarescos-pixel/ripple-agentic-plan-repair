from __future__ import annotations

import os
from typing import Any, Protocol

from ripple.aws.bedrock import TrackedBedrockConverseClient
from ripple.observability.cloudwatch import CloudWatchTraceSink
from ripple.orchestration.agent import GoldenChangeInterpreter
from ripple.orchestration.bedrock_interpreter import BedrockChangeInterpreter


class TraceSink(Protocol):
    def emit(self, event_type: str, *, correlation_id: str, payload=None, timestamp_ms=None): ...


class NoopTraceSink:
    def emit(self, event_type: str, *, correlation_id: str, payload=None, timestamp_ms=None):
        return {
            "schema": "ripple.trace.v1",
            "event_type": event_type,
            "correlation_id": correlation_id,
            "payload": dict(payload or {}),
        }


def build_change_interpreter():
    mode = os.getenv("RIPPLE_CHANGE_INTERPRETER", "golden").strip().lower()
    if mode == "golden":
        return GoldenChangeInterpreter()
    if mode != "bedrock":
        raise RuntimeError(f"Unsupported RIPPLE_CHANGE_INTERPRETER: {mode}")
    model_id = os.getenv("RIPPLE_BEDROCK_MODEL_ID", "").strip()
    if not model_id:
        raise RuntimeError("RIPPLE_BEDROCK_MODEL_ID is required in Bedrock mode")
    region = os.getenv("AWS_REGION", "eu-central-1")
    client = TrackedBedrockConverseClient(region_name=region)
    return BedrockChangeInterpreter(client=client, model_id=model_id)


def build_trace_sink() -> TraceSink:
    backend = os.getenv("RIPPLE_TRACE_BACKEND", "none").strip().lower()
    if backend in {"", "none", "noop"}:
        return NoopTraceSink()
    if backend != "cloudwatch":
        raise RuntimeError(f"Unsupported RIPPLE_TRACE_BACKEND: {backend}")
    group = os.getenv("RIPPLE_CLOUDWATCH_LOG_GROUP", "").strip()
    stream = os.getenv("RIPPLE_CLOUDWATCH_LOG_STREAM", "runtime").strip()
    if not group:
        raise RuntimeError("RIPPLE_CLOUDWATCH_LOG_GROUP is required in CloudWatch mode")
    try:
        import boto3  # type: ignore
    except ImportError as exc:  # pragma: no cover - live AWS only
        raise RuntimeError("Install the aws optional dependencies to use CloudWatch") from exc
    client: Any = boto3.client("logs", region_name=os.getenv("AWS_REGION", "eu-central-1"))
    return CloudWatchTraceSink(client=client, log_group=group, log_stream=stream)
