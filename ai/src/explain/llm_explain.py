"""LLM(Gemini)으로 진단 결과를 쉬운 문장으로 설명한다.

GEMINI_API_KEY 가 없거나 호출에 실패하면 미리 정한 기본 문장을 쓴다.
"""
import os

STATUS_NAMES = {"stable": "안정", "warning": "주의", "danger": "위험(Red Zone)", "unknown": "판단 불가"}
LIFE_STAGE_NAMES = {"youth": "청년", "family": "신혼·육아 가구", "senior": "중장년·노년"}
HOUSE_TYPE_NAMES = {"apartment": "아파트", "officetel": "오피스텔", "house": "단독/다가구", "villa": "연립/다세대"}


def basic_explanation(result):
    """LLM 없이 만드는 기본 설명"""
    status = STATUS_NAMES[result["status"]]
    gap = result["price_gap_percent"]
    if gap > 10:
        price_text = f"비슷한 집의 예상 시세보다 약 {gap}% 비싸게 내고 있습니다."
    elif gap < -10:
        price_text = f"비슷한 집의 예상 시세보다 약 {abs(gap)}% 싸게 내고 있습니다."
    else:
        price_text = "비슷한 집의 예상 시세와 비슷한 수준입니다."
    return (
        f"소득 대비 주거비 비율은 {result['rir_percent']}%로 '{status}' 단계입니다. "
        f"{price_text} "
        "주거비가 소득의 30%를 넘으면 예산 안에서 다른 자치구도 함께 비교해 보세요."
    )


def make_prompt(request, result):
    return "\n".join([
        "너는 서울 주거비 상담 도우미다.",
        "아래 진단 결과를 보고 사용자에게 3문장 이내의 쉬운 한국어로 설명하고, 현실적인 조언 1개를 덧붙여라.",
        "숫자는 그대로 인용하고, 투자 권유나 단정적인 표현은 하지 마라.",
        "",
        f"생애단계: {LIFE_STAGE_NAMES.get(request['life_stage'], request['life_stage'])}",
        f"자치구: {request['district']} / 주택유형: {HOUSE_TYPE_NAMES.get(request['house_type'], request['house_type'])} / 면적: {request['area_m2']}㎡",
        f"월 소득: {request['monthly_income']}만원",
        f"월 환산 주거비: {result['monthly_cost']}만원",
        f"소득 대비 주거비 비율(RIR): {result['rir_percent']}% → {STATUS_NAMES[result['status']]}",
        f"AI 예상 시세(ML {result['ml_price']}만원, DL {result['dl_price']}만원, 평균 {result['market_price']}만원)",
        f"시세 대비 차이: {result['price_gap_percent']}%",
        f"이 구 아파트 회계감사 단지 수(관리 투명도): {result.get('audit_count')}",
    ])


def explain(request, result):
    """(설명 문장, 출처) 를 돌려준다. 출처는 "gemini" 또는 "basic"."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return basic_explanation(result), "basic"

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=15000),  # 15초
        )
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
            contents=make_prompt(request, result),
        )
        if response.text:
            return response.text.strip(), "gemini"
    except Exception as error:
        print("Gemini 호출 실패, 기본 설명을 사용합니다:", type(error).__name__)

    return basic_explanation(result), "basic"
