"""주거 지원 정책에 대한 신청 자격 조건을 확인하는 서비스입니다.

지역, 소득, 생애 단계, 신청 기간 등을 규칙 기반으로 검증하며,
AI가 신청 자격을 임의로 확정하거나 자동 신청하지 않도록 안전장치를 제공합니다.
"""
from typing import List, Dict, Any, Optional
from src.features.housing_rag_001.schemas import UserProfile, PolicyDocument, EligibilityResult

# 임의 확정 방지를 위한 공식 면책 고지 문구
OFFICIAL_DISCLAIMER = (
    "본 결과는 AI 모의 확인 결과이며, 실제 신청 자격을 확정하거나 대리 신청하지 않습니다. "
    "최종 신청 자격과 세부 제출 서류는 주관 기관(SH공사, LH공사, 마이홈 등)의 공식 공고문을 반드시 확인해 주세요."
)


def check_district_match(user_district: str, target_districts: List[str]) -> bool:
    """사용자의 거주 자치구가 정책 지원 대상 지역에 포함되는지 확인합니다.
    
    target_districts가 비어 있으면 서울시 전역을 대상으로 합니다.
    """
    if not target_districts:
        return True
    return user_district in target_districts


def check_income_match(monthly_income: float, income_limit: Optional[float]) -> bool:
    """사용자의 월 소득이 정책의 소득 상한선 이하인지 확인합니다.
    
    income_limit이 None이면 소득 제한이 없는 정책입니다.
    """
    if income_limit is None:
        return True
    return monthly_income <= income_limit


def check_stage_match(user_stage: str, target_stages: List[str]) -> bool:
    """사용자의 생애 단계(청년, 신혼가구, 고령자 등)가 정책 대상에 맞는지 확인합니다."""
    if not target_stages:
        return True
    return user_stage in target_stages


def check_period_active(is_active: bool, period_str: str) -> bool:
    """정책의 신청 기간이 유효한지 확인합니다. 마감되었거나 비활성이면 False를 반환합니다."""
    if not is_active:
        return False
    if "마감" in period_str or "종료" in period_str:
        return False
    return True


def evaluate_eligibility(user: UserProfile, policy: PolicyDocument) -> EligibilityResult:
    """사용자 조건과 정책 공고 조건을 비교하여 신청 가능성을 검증합니다.
    
    절대로 자격을 100% 확정하거나 자동 신청하지 않으며, 가능성 단계로만 안내합니다.
    """
    matched: List[str] = []
    unmatched: List[str] = []
    reasons: List[str] = []

    # 1) 신청 기간 및 활성화 여부 확인
    is_period_ok = check_period_active(policy.is_active, policy.application_period)
    if not is_period_ok:
        unmatched.append(f"신청 기간 마감 ({policy.application_period})")
        reasons.append("해당 정책은 현재 모집 기간이 종료되어 신청이 불가능합니다.")
        return EligibilityResult(
            policy_id=policy.id,
            policy_title=policy.title,
            status="EXPIRED",
            reasons=reasons,
            matched_conditions=matched,
            unmatched_conditions=unmatched,
            disclaimer=OFFICIAL_DISCLAIMER,
            auto_applied=False,
        )

    # 2) 지역 조건 확인
    is_district_ok = check_district_match(user.district, policy.target_districts)
    if is_district_ok:
        district_desc = "서울 전역 대상" if not policy.target_districts else f"{', '.join(policy.target_districts)} 거주자"
        matched.append(f"지역 조건 충족 ({user.district} - {district_desc})")
    else:
        unmatched.append(f"지원 대상 지역 불일치 ({', '.join(policy.target_districts)} 한정)")
        reasons.append(f"이 정책은 {', '.join(policy.target_districts)} 주민을 대상으로 합니다.")

    # 3) 생애 단계 확인
    is_stage_ok = check_stage_match(user.life_stage, policy.target_stages)
    if is_stage_ok:
        matched.append(f"생애 단계 조건 충족 ({user.life_stage})")
    else:
        unmatched.append(f"생애 단계 불일치 (대상: {', '.join(policy.target_stages)})")
        reasons.append(f"해당 정책의 대상 생애 단계({', '.join(policy.target_stages)})와 일치하지 않습니다.")

    # 4) 소득 기준 확인
    is_income_ok = check_income_match(user.monthly_income, policy.income_limit_monthly)
    if is_income_ok:
        limit_desc = f"월 {policy.income_limit_monthly}만원 이하" if policy.income_limit_monthly else "소득 무관"
        matched.append(f"소득 조건 충족 (월 {user.monthly_income}만원 / 기준: {limit_desc})")
    else:
        unmatched.append(f"소득 기준 초과 (신청 기준: 월 {policy.income_limit_monthly}만원 이하)")
        reasons.append(f"월 소득이 {user.monthly_income}만원으로 기준 상한선({policy.income_limit_monthly}만원)을 초과합니다.")

    # 5) 무주택 여부 확인
    if not user.is_homeless:
        unmatched.append("유주택자 (대부분의 공공 주거 정책은 무주택자 대상)")
        reasons.append("공공 주거 지원 정책은 대부분 무주택 세대 구성원을 대상으로 합니다.")

    # 6) 종합 자격 상태 판단
    if not is_district_ok or not is_stage_ok or not is_income_ok or not user.is_homeless:
        status = "INELIGIBLE"
        reasons.append("기본 지원 요건 중 일부가 부합하지 않아 신청이 어려울 수 있습니다.")
    else:
        # 추가 서류나 세부 심사가 필요하므로 CONDITIONAL 또는 ELIGIBLE_PROBABLE 부여
        if user.age and (user.age < 19 or user.age > 39) and "youth" in policy.target_stages:
            status = "CONDITIONAL"
            reasons.append(f"청년 정책의 경우 세부 만 나이 기준(만 19~39세) 확인이 필요합니다 (현재 만 {user.age}세).")
            unmatched.append(f"나이 요건 추가 확인 필요 (만 {user.age}세)")
        else:
            status = "ELIGIBLE_PROBABLE"
            reasons.append("기본 지원 요건(지역, 생애단계, 소득 기준)을 충족하여 신청 가능성이 높습니다.")

    return EligibilityResult(
        policy_id=policy.id,
        policy_title=policy.title,
        status=status,
        reasons=reasons,
        matched_conditions=matched,
        unmatched_conditions=unmatched,
        disclaimer=OFFICIAL_DISCLAIMER,
        auto_applied=False,  # 절대 자동 신청하지 않음
    )
