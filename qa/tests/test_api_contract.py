"""API contract tests for AI domain & Spring Controller/DTO/Exception rules."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai"))

from src.domain.district_stats import all_districts, find_stat, load_stats  # noqa: E402
from src.domain.rir import calculate_rir, classify, monthly_cost  # noqa: E402
from src.explain.llm_explain import basic_explanation, explain  # noqa: E402


def test_ai_rir_and_boundary_contracts(monkeypatch) -> None:
    assert monthly_cost(10000, 0) == 41.7
    assert monthly_cost(0, 0) == 0.0
    assert calculate_rir(0, 100) is None
    assert calculate_rir(-50, 100) is None
    assert classify(None) == ("unknown", False)
    assert classify(0.30) == ("stable", False)
    assert classify(0.3001) == ("warning", False)
    assert classify(0.40) == ("warning", False)
    assert classify(0.4001) == ("danger", True)

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    sample_req = {
        "life_stage": "youth",
        "district": "마포구",
        "house_type": "officetel",
        "area_m2": 30,
        "monthly_income": 300,
    }
    sample_res = {
        "monthly_cost": 84.2,
        "rir_percent": 28.1,
        "status": "stable",
        "ml_price": 90.0,
        "dl_price": 88.0,
        "market_price": 89.0,
        "price_gap_percent": -5.4,
        "audit_count": 10,
    }
    text, source = explain(sample_req, sample_res)
    assert source == "basic"
    assert "28.1%" in text
    assert basic_explanation({**sample_res, "price_gap_percent": 15.0}).find("비싸게") != -1
    assert basic_explanation({**sample_res, "price_gap_percent": -15.0}).find("싸게") != -1


def test_district_stats_and_spring_api_annotations() -> None:
    stats = load_stats()
    assert len(stats) > 0
    districts = all_districts()
    assert len(districts) == 25
    assert find_stat("마포구", "apartment") is not None
    assert find_stat("없는구", "apartment") is None

    diag_ctrl = (
        ROOT / "back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java"
    ).read_text(encoding="utf-8")
    rec_ctrl = (
        ROOT / "back/src/main/java/com/pivotseoul/recommend/controller/RecommendController.java"
    ).read_text(encoding="utf-8")
    err_handler = (
        ROOT / "back/src/main/java/com/pivotseoul/global/exception/GlobalExceptionHandler.java"
    ).read_text(encoding="utf-8")
    diag_dto = (
        ROOT / "back/src/main/java/com/pivotseoul/diagnosis/dto/DiagnosisRequest.java"
    ).read_text(encoding="utf-8")

    assert '@RequestMapping("/api/diagnoses")' in diag_ctrl
    assert "@ResponseStatus(HttpStatus.CREATED)" in diag_ctrl
    assert '@RequestMapping("/api/recommendations")' in rec_ctrl
    for code in ("VALIDATION_ERROR", "INVALID_JSON", "INTERNAL_ERROR"):
        assert code in err_handler
    for rule in ('@Pattern(regexp = "youth|family|senior")', "@NotBlank", "@Positive"):
        assert rule in diag_dto
