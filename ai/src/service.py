"""두 가지 메인 기능의 실제 계산을 담당한다.

1. diagnose  : 내 주거비 진단 (RIR + ML/DL 시세 비교 + LLM 설명)
2. recommend : 예산에 맞는 자치구 추천 (25개 구를 모두 예측해서 정렬)
"""
import pandas as pd

from src.domain.district_stats import all_districts, find_stat
from src.prediction.dl_model import predict_dl
from src.prediction.features import make_input_frame
from src.explain.llm_explain import explain
from src.prediction.ml_model import predict_ml
from src.domain.rir import SAFE_LIMIT, calculate_rir, classify, monthly_cost


def to_int_or_none(value):
    """통계 JSON의 숫자를 int로 바꾼다. 없거나 비어 있으면 None."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def predict_price(input_frame):
    """ML·DL 두 모델의 예측값과 평균값을 함께 돌려준다."""
    ml_prices = predict_ml(input_frame)
    dl_prices = predict_dl(input_frame)
    average = [round((ml + dl) / 2, 1) for ml, dl in zip(ml_prices, dl_prices)]
    return ml_prices, dl_prices, average


def diagnose(request, include_explanation=True):
    """request: 사용자가 입력한 값(딕셔너리)"""
    # 1) 규칙 기반: 내가 실제로 내는 돈으로 RIR 계산
    cost = monthly_cost(request["deposit"], request["monthly_rent"])
    rir = calculate_rir(request["monthly_income"], cost)
    status, is_red_zone = classify(rir)

    # 2) ML·DL: 같은 조건 집의 '적정 시세' 예측
    frame = make_input_frame(
        request["district"], request["house_type"], request["area_m2"],
        request["building_age"], request["floor"],
    )
    ml_prices, dl_prices, average = predict_price(frame)
    market_price = average[0]
    gap_percent = round((cost - market_price) / market_price * 100, 1) if market_price > 0 else 0.0

    stat = find_stat(request["district"], request["house_type"]) or {}

    result = {
        "monthly_cost": cost,
        "rir": rir,
        "rir_percent": round(rir * 100, 1) if rir is not None else None,
        "status": status,
        "is_red_zone": is_red_zone,
        "ml_price": ml_prices[0],
        "dl_price": dl_prices[0],
        "market_price": market_price,
        "price_gap_percent": gap_percent,
        "district_median_cost": stat.get("median_monthly_cost"),
        "district_deal_count": stat.get("deal_count"),
        "audit_count": to_int_or_none(stat.get("audit_count")),
    }

    # 3) LLM: include_explanation이 True일 때만 Gemini 동기 호출
    if include_explanation:
        explanation, source = explain(request, result)
        result["explanation"] = explanation
        result["explanation_source"] = source
    else:
        result["explanation"] = None
        result["explanation_source"] = "pending"

    return result


def generate_explanation(request, result):
    """지표 결과를 바탕으로 LLM 설명을 생성하여 돌려준다."""
    explanation, source = explain(request, result)
    return {
        "explanation": explanation,
        "explanation_source": source,
    }


def recommend(request, limit=5):
    """같은 조건의 집을 25개 구에 놓고 예측해서, 예산(소득의 30%) 안에 드는 구를 싼 순으로 보여준다."""
    districts = all_districts()
    frame = pd.concat(
        [
            make_input_frame(d, request["house_type"], request["area_m2"],
                             request["building_age"], request["floor"])
            for d in districts
        ],
        ignore_index=True,
    )
    _, _, prices = predict_price(frame)

    budget = round(request["monthly_income"] * SAFE_LIMIT, 1)
    items = []
    for district, price in zip(districts, prices):
        rir = calculate_rir(request["monthly_income"], price)
        status, is_red_zone = classify(rir)
        stat = find_stat(district, request["house_type"]) or {}
        items.append({
            "district": district,
            "predicted_cost": price,
            "rir_percent": round(rir * 100, 1) if rir is not None else None,
            "status": status,
            "is_red_zone": is_red_zone,
            "within_budget": price <= budget,
            "deal_count": stat.get("deal_count"),
            "audit_count": to_int_or_none(stat.get("audit_count")),
        })

    items.sort(key=lambda item: item["predicted_cost"])
    return {
        "budget": budget,
        "within_budget_count": sum(item["within_budget"] for item in items),
        "recommendations": items[:limit],
        "all_districts": items,
    }
