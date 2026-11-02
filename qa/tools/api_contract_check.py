#!/usr/bin/env python3
"""Second tool for QA-API-CONTRACT-001.

Verifies AI RIR/stats/explain contract invariants and Spring Controller/DTO/Exception
contracts without using pytest.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai"))

from src.domain.district_stats import all_districts, find_stat  # noqa: E402
from src.domain.rir import calculate_rir, classify, monthly_cost  # noqa: E402
from src.explain.llm_explain import explain  # noqa: E402


def main() -> int:
    failures: list[str] = []

    def expect(name: str, got: object, want: object) -> None:
        if got != want:
            failures.append(f"{name}: got {got!r} want {want!r}")

    expect("cost-jeonse", monthly_cost(10000, 0), 41.7)
    expect("rir-zero-income", calculate_rir(0, 80), None)
    expect("rir-negative-income", calculate_rir(-10, 80), None)
    expect("classify-none", classify(None), ("unknown", False))
    expect("classify-30", classify(0.30), ("stable", False))
    expect("classify-40", classify(0.40), ("warning", False))
    expect("classify-41", classify(0.41), ("danger", True))
    expect("districts-25", len(all_districts()), 25)
    expect("find-stat-missing", find_stat("없는구", "apartment"), None)

    old_key = os.environ.pop("GEMINI_API_KEY", None)
    try:
        text, src = explain(
            {"life_stage": "youth", "district": "마포구", "house_type": "apartment", "area_m2": 59, "monthly_income": 300},
            {
                "monthly_cost": 90.0,
                "rir_percent": 30.0,
                "status": "stable",
                "ml_price": 90.0,
                "dl_price": 90.0,
                "market_price": 90.0,
                "price_gap_percent": 0.0,
                "audit_count": 5,
            },
        )
        expect("explain-fallback-source", src, "basic")
        if "안정" not in text:
            failures.append("explain basic text missing status label")
    finally:
        if old_key is not None:
            os.environ["GEMINI_API_KEY"] = old_key

    checks = [
        ("back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java", '@RequestMapping("/api/diagnoses")'),
        ("back/src/main/java/com/pivotseoul/recommend/controller/RecommendController.java", '@RequestMapping("/api/recommendations")'),
        ("back/src/main/java/com/pivotseoul/global/HealthController.java", '@GetMapping("/api/health")'),
        ("back/src/main/java/com/pivotseoul/global/exception/GlobalExceptionHandler.java", '"VALIDATION_ERROR"'),
        ("back/src/main/java/com/pivotseoul/global/exception/GlobalExceptionHandler.java", '"INVALID_JSON"'),
    ]
    for rel, token in checks:
        content = (ROOT / rel).read_text(encoding="utf-8")
        if token not in content:
            failures.append(f"{rel} missing {token}")

    payload = {
        "status": "FAIL" if failures else "PASS",
        "summary": ", ".join(failures) if failures else "AI RIR/stats/explain & Spring REST API contracts verified",
        "findings": failures,
        "file": "ai/src/domain/rir.py",
        "function": "classify",
        "line_needle": "def classify",
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
