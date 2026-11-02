#!/usr/bin/env python3
"""Second tool for QA-INT-PIPELINE-001.

Independently verifies Data <-> AI <-> Back <-> Front integration invariants without pytest.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ai"))

from data.etl.config import CONVERSION_RATE as DATA_RATE, FALLBACK_DISTRICTS  # noqa: E402
from src.domain.district_stats import all_districts  # noqa: E402
from src.domain.rir import CONVERSION_RATE as AI_RATE  # noqa: E402


def main() -> int:
    failures: list[str] = []

    if DATA_RATE != AI_RATE:
        failures.append(f"conversion rate mismatch: data={DATA_RATE} ai={AI_RATE}")

    d_data = sorted(FALLBACK_DISTRICTS.values())
    d_ai = all_districts()
    front_text = (ROOT / "front/src/components/options.ts").read_text(encoding="utf-8")
    d_front = sorted(re.findall(r'"([가-힣]+구)"', front_text))
    if not (d_data == d_ai == d_front and len(d_data) == 25):
        failures.append("25 districts mismatch across data/ai/front")

    diag_svc = (
        ROOT / "back/src/main/java/com/pivotseoul/diagnosis/service/DiagnosisService.java"
    ).read_text(encoding="utf-8")
    for field in (
        "monthly_cost",
        "rir_percent",
        "is_red_zone",
        "ml_price",
        "dl_price",
        "market_price",
        "price_gap_percent",
        "district_median_cost",
        "audit_count",
        "explanation_source",
    ):
        if f'"{field}"' not in diag_svc:
            failures.append(f"DiagnosisService missing AI field {field}")

    payload = {
        "status": "FAIL" if failures else "PASS",
        "summary": ", ".join(failures) if failures else "Data-AI-Back-Front 25 districts, conversion rate, and schema mapping aligned",
        "findings": failures,
        "file": "back/src/main/java/com/pivotseoul/diagnosis/service/DiagnosisService.java",
        "function": "diagnose",
        "line_needle": "public Diagnosis diagnose(",
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
