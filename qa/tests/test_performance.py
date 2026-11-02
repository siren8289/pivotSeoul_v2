"""Performance benchmark tests for ETL transform and AI RIR/district stats lookup."""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ai"))

from data.etl.transform import calc_monthly_cost, district_from_address  # noqa: E402
from src.domain.district_stats import all_districts, find_stat  # noqa: E402
from src.domain.rir import calculate_rir, classify, monthly_cost  # noqa: E402


def test_etl_and_rir_latency_budget() -> None:
    t0 = time.perf_counter()
    for _ in range(1000):
        calc_monthly_cost(10000, 50)
        district_from_address("서울특별시 마포구 공덕동")
    etl_ms = (time.perf_counter() - t0) * 1000.0
    assert etl_ms < 500.0, f"ETL 1000 iterations too slow: {etl_ms:.2f}ms"

    districts = all_districts()
    t1 = time.perf_counter()
    for _ in range(200):
        for d in districts:
            stat = find_stat(d, "apartment")
            cost = monthly_cost(5000, 80)
            classify(calculate_rir(350, cost))
            assert stat is not None
    ai_ms = (time.perf_counter() - t1) * 1000.0
    assert ai_ms < 1000.0, f"AI 5000 district evaluations too slow: {ai_ms:.2f}ms"
