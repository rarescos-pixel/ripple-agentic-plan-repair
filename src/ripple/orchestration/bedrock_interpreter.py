from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Dict, Protocol

from ripple.domain.models import ChangeEvent
from ripple.policy.cost import ModelBudget


class BedrockConverseClient(Protocol):
    def converse(self, **kwargs): ...


RECORD_CHANGE_TOOL = {
    "tools": [{
        "toolSpec": {
            "name": "record_change",
            "description": "Normalize exactly one user-reported change to an existing plan fact. Do not execute or repair anything.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "node_id": {"type": "string", "description": "Existing canonical node id from allowed_nodes."},
                        "field": {"type": "string", "description": "Existing mutable field from allowed_fields."},
                        "new_value": {"type": "string", "description": "Normalized new value, ISO-8601 for date/time fields."},
                        "confidence": {"type": "number", "description": "Confidence from 0 to 1."},
                    },
                    "required": ["node_id", "field", "new_value", "confidence"],
                }
            },
        }
    }],
    "toolChoice": {"tool": {"name": "record_change"}},
}


def _canonical_change_id(*, node_id: str, field: str, old_value: Any, new_value: str) -> str:
    """Stable semantic identity used by downstream idempotency keys.

    Bedrock may normalize the same utterance more than once, or a user may
    report a later, genuinely different change to the same fact. Identity must
    therefore be stable for the same canonical transition and different when
    the transition changes. It must never depend on model wording, confidence,
    request timing, or an ephemeral MCP session id.
    """
    material = json.dumps(
        {
            "node_id": node_id,
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
        },
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    digest = hashlib.sha256(material.encode()).hexdigest()[:20]
    return f"change:bedrock:{digest}"


@dataclass
class BedrockChangeInterpreter:
    client: BedrockConverseClient
    model_id: str = "eu.amazon.nova-2-lite-v1:0"
    budget: ModelBudget = ModelBudget()

    def interpret(self, utterance: str, context: Dict[str, Any]) -> ChangeEvent:
        allowed_nodes = context.get("allowed_nodes", {"flight:return": {"arrival_at": context.get("old_arrival_at")}})
        allowed_fields = context.get("allowed_fields", {"flight:return": ["arrival_at"]})
        canonical = json.dumps({"allowed_nodes": allowed_nodes, "allowed_fields": allowed_fields}, sort_keys=True, default=str)
        self.budget.validate_input(utterance, canonical)
        correlation_id = str(context.get("correlation_id", "bedrock"))[:256]

        response = self.client.converse(
            modelId=self.model_id,
            system=[{"text": (
                "You normalize one changed fact for Ripple. Use only canonical node ids and mutable fields supplied by the application. "
                "Never propose repairs, never call external services, and never invent the old value. Call record_change exactly once."
            )}],
            messages=[{"role": "user", "content": [{"text": f"CANONICAL_CONTEXT={canonical}\nUSER_CHANGE={utterance}"}]}],
            toolConfig=RECORD_CHANGE_TOOL,
            inferenceConfig={"maxTokens": self.budget.max_output_tokens, "temperature": 0},
            requestMetadata={"ripple_correlation_id": correlation_id},
        )
        blocks = response.get("output", {}).get("message", {}).get("content", [])
        tool_uses = [b["toolUse"] for b in blocks if "toolUse" in b]
        if len(tool_uses) != 1 or tool_uses[0].get("name") != "record_change":
            raise ValueError("Bedrock interpreter must return exactly one record_change tool call")
        data = tool_uses[0].get("input", {})
        node_id = data.get("node_id")
        field = data.get("field")
        new_value = data.get("new_value")
        confidence = float(data.get("confidence", 0))

        if node_id not in allowed_nodes:
            raise ValueError("Model returned a node outside canonical context")
        if field not in allowed_fields.get(node_id, []):
            raise ValueError("Model returned a field outside canonical context")
        if not isinstance(new_value, str) or not new_value:
            raise ValueError("Model returned an invalid new value")
        if not 0 <= confidence <= 1:
            raise ValueError("Model returned invalid confidence")
        if confidence < float(context.get("minimum_confidence", 0.80)):
            raise ValueError("Model confidence below execution-planning threshold")

        old_value = allowed_nodes[node_id].get(field)
        if old_value is None:
            raise ValueError("Canonical old value is missing")
        change_id = context.get("change_id") or _canonical_change_id(
            node_id=node_id,
            field=field,
            old_value=old_value,
            new_value=new_value,
        )
        return ChangeEvent(
            id=change_id,
            node_id=node_id,
            field=field,
            old_value=old_value,
            new_value=new_value,
            source="voice",
            confidence=confidence,
            correlation_id=correlation_id,
        )
