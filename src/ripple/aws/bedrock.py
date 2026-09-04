from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TrackedBedrockConverseClient:
    """Thin boto3 Converse adapter that exposes usage for evaluation.

    boto3 is imported lazily so the core deterministic engine remains usable
    without AWS credentials or an AWS SDK installation.
    """

    region_name: str = "eu-central-1"
    client: Any | None = None
    last_usage: dict[str, int] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        if self.client is None:
            try:
                import boto3  # type: ignore
            except ImportError as exc:  # pragma: no cover - live AWS only
                raise RuntimeError("Install the aws optional dependencies to use Bedrock") from exc
            self.client = boto3.client("bedrock-runtime", region_name=self.region_name)

    def converse(self, **kwargs):
        response = self.client.converse(**kwargs)
        usage = response.get("usage") or {}
        self.last_usage = {
            "inputTokens": int(usage.get("inputTokens", 0)),
            "outputTokens": int(usage.get("outputTokens", 0)),
        }
        return response
