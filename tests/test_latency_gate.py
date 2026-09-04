import pytest

from ripple.evaluation.latency import latency_gate, summarize_latencies


def test_latency_summary_requires_every_sample_under_alexa_limit():
    stats = summarize_latencies("preview", [101, 120, 130, 140, 499.9], limit_ms=500)
    assert stats.samples == 5
    assert stats.p50_ms == 130
    assert stats.p95_ms == 499.9
    assert stats.max_ms == 499.9
    assert stats.under_limit == 5
    assert stats.passed is True


def test_latency_summary_fails_on_single_500ms_or_slower_round_trip():
    stats = summarize_latencies("record_change", [90, 100, 500], limit_ms=500)
    assert stats.under_limit == 2
    assert stats.passed is False
    assert latency_gate([stats]) is False


def test_latency_gate_requires_all_operations_to_pass():
    fast = summarize_latencies("ping", [10, 12, 14], limit_ms=500)
    slow = summarize_latencies("preview", [100, 510, 120], limit_ms=500)
    assert latency_gate([fast]) is True
    assert latency_gate([fast, slow]) is False
    assert latency_gate([]) is False


def test_latency_summary_rejects_invalid_input():
    with pytest.raises(ValueError, match="at least one"):
        summarize_latencies("ping", [], limit_ms=500)
    with pytest.raises(ValueError, match="positive"):
        summarize_latencies("ping", [10], limit_ms=0)
