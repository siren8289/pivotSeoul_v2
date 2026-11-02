"""Cross-layer integration tests across Data ETL, AI, Spring Backend, and React Frontend."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ai"))

from data.etl.config import CONVERSION_RATE as DATA_RATE, FALLBACK_DISTRICTS, RENT_APIS  # noqa: E402
from src.domain.district_stats import all_districts  # noqa: E402
from src.domain.rir import CONVERSION_RATE as AI_RATE  # noqa: E402
from src.prediction.features import CATEGORY_COLUMNS, NUMBER_COLUMNS  # noqa: E402


def test_cross_layer_constants_and_districts() -> None:
    assert DATA_RATE == AI_RATE == 0.05

    data_districts = sorted(FALLBACK_DISTRICTS.values())
    ai_districts = all_districts()
    front_opt = (ROOT / "front/src/components/options.ts").read_text(encoding="utf-8")
    front_districts = sorted(re.findall(r'"([가-힣]+구)"', front_opt))

    assert len(data_districts) == 25
    assert data_districts == ai_districts == front_districts

    data_house_types = sorted(item["house_type"] for item in RENT_APIS.values())
    assert data_house_types == ["apartment", "house", "officetel", "villa"]
    assert CATEGORY_COLUMNS == ["district", "house_type"]
    assert NUMBER_COLUMNS == ["area_m2", "building_age", "floor"]


def test_back_to_ai_and_front_field_mapping() -> None:
    diag_service = (
        ROOT / "back/src/main/java/com/pivotseoul/diagnosis/service/DiagnosisService.java"
    ).read_text(encoding="utf-8")
    rec_service = (
        ROOT / "back/src/main/java/com/pivotseoul/recommend/service/RecommendService.java"
    ).read_text(encoding="utf-8")
    front_api = (ROOT / "front/src/api/api.ts").read_text(encoding="utf-8")

    for snake in (
        "life_stage",
        "district",
        "house_type",
        "area_m2",
        "building_age",
        "floor",
        "monthly_income",
        "deposit",
        "monthly_rent",
    ):
        assert f'"{snake}"' in diag_service

    for ai_field in (
        "monthly_cost",
        "rir_percent",
        "status",
        "is_red_zone",
        "ml_price",
        "dl_price",
        "market_price",
        "price_gap_percent",
        "district_median_cost",
        "audit_count",
        "explanation",
        "explanation_source",
    ):
        assert f'"{ai_field}"' in diag_service

    for rec_snake in ("life_stage", "house_type", "area_m2", "building_age", "floor", "monthly_income"):
        assert f'"{rec_snake}"' in rec_service

    for ts_field in (
        "monthlyCost",
        "rirPercent",
        "redZone",
        "mlPrice",
        "dlPrice",
        "marketPrice",
        "priceGapPercent",
        "districtMedianCost",
        "auditCount",
        "explanation",
        "explanationSource",
    ):
        assert ts_field in front_api
