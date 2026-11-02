#!/usr/bin/env python3
"""Second tool for QA-PERF-BENCH-001.

Measures throughput/latency of ETL and AI RIR/district-stats computations without pytest.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ai"))

from data.etl.transform import calc_monthly_cost, district_from_address  # noqa: E402
from src.domain.district_stats import all_districts, find_stat  # noqa: E402
from src.domain.rir import calculate_rir, classify, monthly_cost  # noqa: E402


def main() -> int:
    failures: list[str] = []

    t0 = time.perf_counter()
    for _ in range(1000):
        calc_monthly_cost(10000, 50)
        district_from_address("서울특별시 마포구 공덕동")
    etl_ms = (time.perf_counter() - t0) * 1000.0
    if etl_ms >= 500.0:
        failures.append(f"etl_ms={etl_ms:.1f} >= 500ms")

    districts = all_districts()
    t1 = time.perf_counter()
    for _ in range(200):
        for d in districts:
            find_stat(d, "apartment")
            cost = monthly_cost(5000, 80)
            classify(calculate_rir(350, cost))
    ai_ms = (time.perf_counter() - t1) * 1000.0
    if ai_ms >= 1000.0:
        failures.append(f"ai_ms={ai_ms:.1f} >= 1000ms")

    payload = {
        "status": "FAIL" if failures else "PASS",
        "summary": ", ".join(failures) if failures else f"etl_1000={etl_ms:.1f}ms (<500ms), ai_5000={ai_ms:.1f}ms (<1000ms)",
        "findings": failures,
        "file": "ai/src/domain/district_stats.py",
        "function": "find_stat",
        "line_needle": "def find_stat",
    }
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001
        json.dump({"status": "ERROR", "summary": str(error), "findings": []}, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        raise SystemExit(1)
