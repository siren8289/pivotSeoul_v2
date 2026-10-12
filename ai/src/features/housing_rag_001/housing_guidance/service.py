"""RIR 주거비 진단 결과와 검색된 정책 근거를 결합하여 맞춤형 정책 설명과 인용을 생성하는 서비스입니다.

LLM(Gemini) 호출을 지원하며, 키가 없거나 실패 시 신뢰할 수 있는 규칙 기반 안내문을 제공합니다.
"""
import os
from typing import List, Dict, Any, Optional
from src.features.housing_rag_001.schemas import UserProfile, EligibilityResult, SearchResultItem, PolicyDocument
from src.domain.rir import calculate_rir, classify, monthly_cost

STATUS_KOREAN = {
    "stable": "안정",
    "warning": "주의",
    "danger": "위험(Red Zone)",
    "unknown": "판단 불가",
}


def compute_user_rir_info(user: UserProfile) -> Dict[str, Any]:
    """사용자의 보증금, 월세, 월소득을 기반으로 RIR 주거비 부담 수준을 계산합니다."""
    cost = monthly_cost(user.deposit, user.monthly_rent)
    rir = calculate_rir(user.monthly_income, cost)
    status, is_red_zone = classify(rir)
    rir_pct = round(rir * 100, 1) if rir is not None else None
    return {
        "monthly_cost": cost,
        "rir": rir,
        "rir_percent": rir_pct,
        "status": status,
        "status_korean": STATUS_KOREAN.get(status, status),
        "is_red_zone": is_red_zone,
    }


def build_fallback_explanation(
    user: UserProfile,
    rir_info: Optional[Dict[str, Any]],
    recommended_policies: List[Dict[str, Any]],
) -> str:
    """LLM API를 호출하지 못할 때 사용하는 신뢰할 수 있는 규칙 기반 정책 설명문입니다."""
    lines = []
    
    # 1) 주거비 부담 상태 안내
    if rir_info and rir_info.get("rir_percent") is not None:
        status_kor = rir_info.get("status_korean", "안정")
        pct = rir_info.get("rir_percent")
        cost = rir_info.get("monthly_cost")
        lines.append(
            f"현재 거주지의 월 환산 주거비는 약 {cost}만원으로, "
            f"월 소득 대비 주거비 비율(RIR)은 {pct}%('{status_kor}' 단계)입니다."
        )
        if rir_info.get("is_red_zone"):
            lines.append("주거비 부담이 40%를 초과하는 위험(Red Zone) 단계이므로 주거비 경감 정책의 지원이 시급합니다.")

    # 2) 추천 정책 요약
    eligible_policies = [p for p in recommended_policies if p["eligibility"]["status"] == "ELIGIBLE_PROBABLE"]
    if eligible_policies:
        top_policy = eligible_policies[0]["policy"]
        lines.append(
            f"사용자님의 조건(지역: {user.district}, 소득: {user.monthly_income}만원)에 가장 부합하는 정책은 "
            f"'{top_policy.title}'({top_policy.organization})입니다. {top_policy.benefit_summary} 혜택을 확인하실 수 있습니다."
        )
    elif recommended_policies:
        top_policy = recommended_policies[0]["policy"]
        lines.append(
            f"추천된 '{top_policy.title}'의 경우 신청 요건 중 일부 추가 서류 확인이 필요할 수 있습니다."
        )
    else:
        lines.append("현재 조건에 일치하는 활성 주거 지원 정책을 찾지 못했습니다.")

    # 3) 행동 조언
    lines.append(
        "각 정책의 세부 신청 일정과 자격 요건은 반드시 아래 공식 출처 링크를 통해 확인해 주시기 바랍니다."
    )
    return " ".join(lines)


def make_guidance_prompt(
    user: UserProfile,
    rir_info: Optional[Dict[str, Any]],
    recommended_policies: List[Dict[str, Any]],
) -> str:
    """Gemini LLM에게 제공할 프롬프트 문자열을 생성합니다."""
    prompt_lines = [
        "너는 서울시 맞춤형 주거 지원 정책 전문 상담사다.",
        "제공된 사용자의 주거비(RIR) 진단 결과와 추천 주거 정책 공고 근거를 바탕으로 쉬운 한국어로 맞춤형 조언을 작성해라.",
        "규칙:",
        "1. 3~4문장 이내로 명확하고 친절하게 설명할 것.",
        "2. 정책 이름과 혜택을 명확히 인용할 것.",
        "3. AI가 신청 자격을 최종 확정하지 않으며, 공식 공고문을 확인해야 한다는 점을 안내할 것.",
        "",
        f"[사용자 프로필] 자치구: {user.district}, 생애단계: {user.life_stage}, 월소득: {user.monthly_income}만원, 무주택여부: {'무주택' if user.is_homeless else '유주택'}",
    ]

    if rir_info:
        prompt_lines.append(
            f"[주거비 진단] 월 환산 주거비: {rir_info.get('monthly_cost')}만원, "
            f"RIR: {rir_info.get('rir_percent')}% ({rir_info.get('status_korean')})"
        )

    prompt_lines.append("[추천 정책 목록]")
    for idx, item in enumerate(recommended_policies, start=1):
        p: PolicyDocument = item["policy"]
        e: EligibilityResult = item["eligibility"]
        prompt_lines.append(
            f"{idx}. {p.title} (기관: {p.organization}) - 혜택: {p.benefit_summary} / 판정결과: {e.status}"
        )

    return "\n".join(prompt_lines)


def generate_guidance_explanation(
    user: UserProfile,
    rir_info: Optional[Dict[str, Any]],
    recommended_policies: List[Dict[str, Any]],
) -> str:
    """RIR 분석 결과와 정책 근거를 결합한 설명 문장을 생성합니다."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=15000),
            )
            prompt = make_guidance_prompt(user, rir_info, recommended_policies)
            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
                contents=prompt,
            )
            if response.text:
                return response.text.strip()
        except Exception:
            # 외부 API 호출 실패 시 템플릿 기반으로 폴백
            pass

    return build_fallback_explanation(user, rir_info, recommended_policies)


def extract_citations(recommended_policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """추천된 정책들로부터 신뢰할 수 있는 공식 출처 및 인용 정보를 추출합니다."""
    citations = []
    seen_urls = set()
    for item in recommended_policies:
        policy: PolicyDocument = item["policy"]
        if policy.source_url not in seen_urls:
            seen_urls.add(policy.source_url)
            citations.append({
                "policy_id": policy.id,
                "title": policy.title,
                "organization": policy.organization,
                "source_url": policy.source_url,
                "support_type": policy.support_type,
                "benefit_summary": policy.benefit_summary,
                "application_period": policy.application_period,
            })
    return citations
