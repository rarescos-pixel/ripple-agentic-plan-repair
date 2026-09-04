from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelBudget:
    """Hard local budget for one interpretation request.

    Ripple uses the model only to normalize a changed fact. Dependency
    traversal, repair choice validation, approvals, and writes stay local and
    deterministic, so one user change should require one model call.
    """
    max_calls_per_proposal: int = 1
    max_input_chars: int = 8000
    max_output_tokens: int = 256

    def validate_input(self, utterance: str, context_text: str) -> None:
        if len(utterance) + len(context_text) > self.max_input_chars:
            raise ValueError("Model input exceeds cost budget")
