from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Iterable


@dataclass(frozen=True)
class LatencyStats:
    operation: str
    samples: int
    limit_ms: float
    p50_ms: float
    p95_ms: float
    max_ms: float
    under_limit: int
    passed: bool

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _nearest_rank(values: list[float], percentile: float) -> float:
    if not values:
        raise ValueError("at least one latency sample is required")
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return ordered[min(rank - 1, len(ordered) - 1)]


def summarize_latencies(operation: str, samples_ms: Iterable[float], *, limit_ms: float = 500.0) -> LatencyStats:
    values = [float(v) for v in samples_ms]
    if not values:
        raise ValueError("at least one latency sample is required")
    if limit_ms <= 0:
        raise ValueError("latency limit must be positive")
    under = sum(1 for value in values if value < limit_ms)
    return LatencyStats(
        operation=operation,
        samples=len(values),
        limit_ms=float(limit_ms),
        p50_ms=_nearest_rank(values, 0.50),
        p95_ms=_nearest_rank(values, 0.95),
        max_ms=max(values),
        under_limit=under,
        passed=under == len(values),
    )


def latency_gate(stats: Iterable[LatencyStats]) -> bool:
    rows = list(stats)
    return bool(rows) and all(row.passed for row in rows)
