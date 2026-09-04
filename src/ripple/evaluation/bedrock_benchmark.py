from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import statistics
import time
from typing import Any, Callable, Iterable

from ripple.orchestration.bedrock_interpreter import BedrockChangeInterpreter


DEFAULT_MODELS = (
    "eu.amazon.nova-lite-v1:0",
    "eu.amazon.nova-2-lite-v1:0",
)


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    utterance: str
    context: dict[str, Any]
    expected: dict[str, Any]


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    passed: bool
    latency_ms: float
    input_tokens: int
    output_tokens: int
    error: str | None = None


@dataclass(frozen=True)
class ModelResult:
    model_id: str
    passed: int
    total: int
    accuracy: float
    median_latency_ms: float
    input_tokens: int
    output_tokens: int
    cases: list[CaseResult]


def load_cases(path: str | Path) -> list[BenchmarkCase]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [BenchmarkCase(**item) for item in data]


def _usage(client: Any) -> tuple[int, int]:
    usage = getattr(client, "last_usage", None) or {}
    return int(usage.get("inputTokens", 0)), int(usage.get("outputTokens", 0))


def evaluate_model(
    model_id: str,
    cases: Iterable[BenchmarkCase],
    client_factory: Callable[[str], Any],
) -> ModelResult:
    results: list[CaseResult] = []
    for case in cases:
        client = client_factory(model_id)
        interpreter = BedrockChangeInterpreter(client=client, model_id=model_id)
        started = time.perf_counter()
        error = None
        passed = False
        try:
            change = interpreter.interpret(case.utterance, dict(case.context))
            observed = {
                "node_id": change.node_id,
                "field": change.field,
                "new_value": change.new_value,
            }
            passed = observed == case.expected
        except Exception as exc:  # benchmark records failures instead of hiding them
            error = f"{type(exc).__name__}: {exc}"
        latency_ms = (time.perf_counter() - started) * 1000
        input_tokens, output_tokens = _usage(client)
        results.append(CaseResult(
            case_id=case.id,
            passed=passed,
            latency_ms=round(latency_ms, 3),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            error=error,
        ))
    total = len(results)
    passed_count = sum(r.passed for r in results)
    latencies = [r.latency_ms for r in results]
    return ModelResult(
        model_id=model_id,
        passed=passed_count,
        total=total,
        accuracy=(passed_count / total) if total else 0.0,
        median_latency_ms=round(statistics.median(latencies), 3) if latencies else 0.0,
        input_tokens=sum(r.input_tokens for r in results),
        output_tokens=sum(r.output_tokens for r in results),
        cases=results,
    )


def rank(results: Iterable[ModelResult]) -> list[ModelResult]:
    """Quality dominates; token volume and latency only break equal-quality ties."""
    return sorted(
        results,
        key=lambda r: (-r.accuracy, r.input_tokens + r.output_tokens, r.median_latency_ms, r.model_id),
    )


def render_markdown(results: Iterable[ModelResult]) -> str:
    ordered = rank(results)
    lines = [
        "# Ripple Bedrock normalizer benchmark",
        "",
        "Quality is the primary selection criterion. Token volume and latency are tie-breakers; no live price is hard-coded.",
        "",
        "| Model | Accuracy | Median latency | Input tokens | Output tokens |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in ordered:
        lines.append(
            f"| `{r.model_id}` | {r.passed}/{r.total} ({r.accuracy:.0%}) | {r.median_latency_ms:.1f} ms | {r.input_tokens} | {r.output_tokens} |"
        )
    if ordered:
        lines += ["", f"Recommended by benchmark policy: **`{ordered[0].model_id}`**"]
    lines += [
        "",
        "This report is meaningful only when produced from real Bedrock calls. Fake-client CI validates the harness contract, not model quality.",
        "",
    ]
    return "\n".join(lines)


def as_json(results: Iterable[ModelResult]) -> str:
    return json.dumps([asdict(r) for r in rank(results)], indent=2, sort_keys=True)
