from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_housing_analyze_prd_acceptance() -> None:
    response = client.post(
        "/api/v1/housing/analyze",
        json={
            "district": "서울특별시 마포구",
            "monthly_income": 5_000_000,
            "monthly_housing_cost": 2_250_000,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["district"] == "마포구"
    assert body["rir"] == 0.45
    assert body["is_red_zone"] is True
    assert body["housing_status"] == "danger"
    assert body["risk_score"] == 80


def test_housing_analyze_rejects_negative_income() -> None:
    response = client.post(
        "/api/v1/housing/analyze",
        json={
            "district": "마포구",
            "monthly_income": -1,
            "monthly_housing_cost": 1_000_000,
        },
    )
    assert response.status_code == 422
