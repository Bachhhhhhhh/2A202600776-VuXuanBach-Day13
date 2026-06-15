from app.dashboard import _is_firing
from app.metrics import percentile


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_high_latency_alert() -> None:
    values = {"latency_p95": 5501, "error_rate_pct": 0, "total_cost_usd": 0}
    assert _is_firing("high_latency_p95", values)
