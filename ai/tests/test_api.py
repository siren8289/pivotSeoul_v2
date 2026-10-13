"""AI 서버 테스트. 실행: cd ai && python -m pytest

GEMINI_API_KEY 를 비워서 LLM 대신 기본 설명이 나오는지 확인한다.
"""
from fastapi.testclient import TestClient

from src.api.main import app
from src.domain.rir import calculate_rir, classify, monthly_cost

client = TestClient(app)


def test_rir_rules():
    assert monthly_cost(10000, 0) == 41.7           # 보증금 1억 전세
    assert classify(calculate_rir(300, 90)) == ("stable", False)    # 30%
    assert classify(calculate_rir(300, 110)) == ("warning", False)  # 36.7%
    assert classify(calculate_rir(300, 150)) == ("danger", True)    # 50%
    assert calculate_rir(0, 100) is None


def test_diagnose(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.post("/api/v1/diagnose", json={
        "life_stage": "youth", "district": "마포구", "house_type": "officetel",
        "area_m2": 30, "building_age": 10, "floor": 5,
        "monthly_income": 300, "deposit": 1000, "monthly_rent": 80,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["monthly_cost"] == 84.2
    assert body["status"] == "stable"
    assert body["ml_price"] > 0 and body["dl_price"] > 0
    assert body["explanation_source"] == "basic"


def test_diagnose_fast_mode():
    """include_explanation=False 일 때 LLM 호출 없이 빠르게 지표만 반환하는지 검증"""
    req_body = {
        "life_stage": "youth", "district": "마포구", "house_type": "officetel",
        "area_m2": 30, "building_age": 10, "floor": 5,
        "monthly_income": 300, "deposit": 1000, "monthly_rent": 80,
        "include_explanation": False,
    }
    response = client.post("/api/v1/diagnose", json=req_body)
    assert response.status_code == 200
    body = response.json()
    assert body["monthly_cost"] == 84.2
    assert body["explanation"] is None
    assert body["explanation_source"] == "pending"


def test_explain_endpoint(monkeypatch):
    """지표 결과를 넘겨 설명만 생성하는 /api/v1/explain 엔드포인트 검증"""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    user_req = {
        "life_stage": "youth", "district": "마포구", "house_type": "officetel",
        "area_m2": 30, "building_age": 10, "floor": 5,
        "monthly_income": 300, "deposit": 1000, "monthly_rent": 80,
    }
    result_metrics = {
        "monthly_cost": 84.2, "status": "stable", "price_gap_percent": -5.4,
        "rir_percent": 28.1, "ml_price": 90.0, "dl_price": 88.0, "market_price": 89.0,
    }
    response = client.post("/api/v1/explain", json={
        "request": user_req,
        "result": result_metrics,
    })
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    assert data["explanation_source"] == "basic"
    assert "안정" in data["explanation"]


def test_recommend():
    response = client.post("/api/v1/recommend", json={
        "house_type": "apartment", "area_m2": 59, "monthly_income": 500,
    })
    assert response.status_code == 200
    body = response.json()
    assert len(body["all_districts"]) == 25
    costs = [item["predicted_cost"] for item in body["all_districts"]]
    assert costs == sorted(costs)   # 싼 순서로 정렬


def test_invalid_input():
    response = client.post("/api/v1/diagnose", json={"district": "마포구", "area_m2": 0})
    assert response.status_code == 422
