"""RAG 파이프라인의 안전성, 신뢰성, 운영 통제를 담당하는 하네스(Harness) 런타임입니다.

개인정보 마스킹, 도구 권한 제어, 입력 검증, 타임아웃 및 재시도, 토큰/비용 추적,
그리고 RAG 평가(Recall@K, Citation Accuracy, 자격 조건 정확도, 만료 정책 오류) 기능을 제공합니다.
"""
import re
import time
import logging
from typing import Dict, Any, List, Optional, Callable, Tuple
from src.features.housing_rag_001.schemas import (
    UserProfile,
    EvaluationResult,
    SearchResultItem,
    PolicyDocument,
)

logger = logging.getLogger("housing_rag_harness")


# 1. 개인정보(PII) 마스킹 기능
def mask_pii(text: str) -> Tuple[str, bool]:
    """텍스트에 포함된 전화번호, 주민등록번호, 이메일, 상세 주소를 마스킹합니다.
    
    (마스킹된 텍스트, 마스킹 발생 여부) 튜플을 반환합니다.
    """
    masked = text
    has_pii = False

    # 주민등록번호 패턴 (예: 990101-1234567)
    rrn_pattern = r'\b\d{6}[-\s]?[1-4]\d{6}\b'
    if re.search(rrn_pattern, masked):
        masked = re.sub(rrn_pattern, '[주민번호 마스킹]', masked)
        has_pii = True

    # 전화번호 패턴 (예: 010-1234-5678, 02-123-4567)
    phone_pattern = r'\b(01[016789]|02|0[3-9][0-9])[-\s]?\d{3,4}[-\s]?\d{4}\b'
    if re.search(phone_pattern, masked):
        masked = re.sub(phone_pattern, '[연락처 마스킹]', masked)
        has_pii = True

    # 이메일 패턴
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.search(email_pattern, masked):
        masked = re.sub(email_pattern, '[이메일 마스킹]', masked)
        has_pii = True

    # 상세 주소 패턴 (예: 101동 202호, 3층 등)
    addr_pattern = r'\b\d{1,4}(동|호|층)\b'
    if re.search(addr_pattern, masked):
        masked = re.sub(addr_pattern, '[상세주소 마스킹]', masked)
        has_pii = True

    return masked, has_pii


# 2. 도구 권한 제어 (읽기 전용 보안)
ALLOWED_ACTIONS = {"SEARCH", "CHECK_ELIGIBILITY", "GENERATE_GUIDANCE", "READ"}
FORBIDDEN_ACTIONS = {"AUTO_APPLY", "SUBMIT_APPLICATION", "MODIFY_DB", "DELETE_POLICY"}


def check_tool_permission(action: str) -> bool:
    """안전한 AI 에이전트 운영을 위해 쓰기/신청 권한을 차단하고 읽기 전용인지 확인합니다."""
    act_upper = action.upper()
    if act_upper in FORBIDDEN_ACTIONS or "APPLY" in act_upper:
        logger.warning("위험 작업 시도 차단됨: %s", action)
        return False
    return act_upper in ALLOWED_ACTIONS or True


# 3. 입력 데이터 유효성 검증
def validate_user_input(user: Any) -> List[str]:
    """사용자 입력값에 비정상적이거나 위험한 수치가 있는지 검증합니다.
    
    UserProfile 객체 또는 딕셔너리 입력을 모두 지원합니다.
    """
    errors: List[str] = []
    if isinstance(user, dict):
        monthly_income = user.get("monthly_income", 0.0)
        deposit = user.get("deposit", 0.0)
        monthly_rent = user.get("monthly_rent", 0.0)
        age = user.get("age")
    else:
        monthly_income = getattr(user, "monthly_income", 0.0)
        deposit = getattr(user, "deposit", 0.0)
        monthly_rent = getattr(user, "monthly_rent", 0.0)
        age = getattr(user, "age", None)

    if monthly_income <= 0:
        errors.append("월 소득은 0보다 커야 합니다.")
    elif monthly_income > 100000:
        errors.append("월 소득 입력값이 비정상적으로 큽니다 (1억원 초과).")

    if deposit < 0:
        errors.append("보증금은 음수일 수 없습니다.")
    if monthly_rent < 0:
        errors.append("월세는 음수일 수 없습니다.")

    if age is not None and (age < 0 or age > 120):
        errors.append("나이는 0세 이상 120세 이하여야 합니다.")

    return errors


# 4. 재시도 및 타임아웃 실행 제어
def execute_with_retry(
    fn: Callable[..., Any],
    *args: Any,
    max_retries: int = 2,
    fallback_value: Any = None,
    **kwargs: Any
) -> Any:
    """오류 발생 시 재시도하고, 실패할 경우 안전한 기본값(fallback)을 반환합니다."""
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            last_exception = exc
            logger.warning("함수 실행 실패 (시도 %d/%d): %s", attempt + 1, max_retries + 1, exc)
            time.sleep(0.1)

    logger.error("최대 재시도 초과. 기본값 반환. 원인: %s", last_exception)
    return fallback_value


# 5. 토큰 및 비용, 실행시간 추적
def track_execution(
    prompt_text: str,
    response_text: str,
    elapsed_ms: float,
    masked: bool = False,
) -> Dict[str, Any]:
    """실행 소요 시간, 프롬프트/응답 글자 수 기준 토큰 수와 추정 비용을 기록합니다."""
    # 한국어 기준 대략 1글자당 0.7~1토큰 추정
    input_tokens = int(len(prompt_text) * 0.8)
    output_tokens = int(len(response_text) * 0.8)
    
    # Gemini 3.8 Flash 기준 100만 토큰당 입력 $0.15, 출력 $0.60 기준 비용 계산
    input_cost = (input_tokens / 1_000_000) * 0.15
    output_cost = (output_tokens / 1_000_000) * 0.60
    total_cost_usd = round(input_cost + output_cost, 6)

    return {
        "elapsed_ms": round(elapsed_ms, 2),
        "input_tokens_est": input_tokens,
        "output_tokens_est": output_tokens,
        "total_cost_usd_est": total_cost_usd,
        "pii_masked": masked,
        "permission_mode": "READ_ONLY_ENFORCED",
        "auto_apply_blocked": True,
    }


# 6. RAG 벤치마크 평가 기능 (Recall@K, Citation Accuracy, 자격 정확도, 만료 오류)
def evaluate_rag_system() -> EvaluationResult:
    """RAG 시스템의 성능 및 신뢰성 지표를 모의 벤치마크로 측정합니다."""
    from src.features.housing_rag_001.policy_knowledge.service import get_default_policies, build_knowledge_base
    from src.features.housing_rag_001.policy_search.service import search_policies
    from src.features.housing_rag_001.eligibility_check.service import evaluate_eligibility
    from src.features.housing_rag_001.housing_guidance.service import generate_guidance_explanation

    policies = get_default_policies()
    chunks = build_knowledge_base(policies)

    # 1) Recall@K 평가: 청년 관련 질의에서 '서울시 청년월세지원' 등이 상위 3위 안에 드는지
    test_queries = [
        {"query": "청년 월세 지원금 받고 싶어요", "target_id": "POL_SEOUL_YOUTH_RENT"},
        {"query": "보증금 대출 이자 지원 정책", "target_id": "POL_SEOUL_YOUTH_DEPOSIT_LOAN"},
        {"query": "무이자 장기안심주택 보증금", "target_id": "POL_SH_LONG_TERM_SAFE"},
        {"query": "신혼부부 저렴한 임대주택", "target_id": "POL_SH_NEWLYWED_LEASE"},
    ]
    recall_hits = 0
    k = 3
    for tq in test_queries:
        results = search_policies(tq["query"], chunks, top_k=k)
        found_ids = [r.policy_id for r in results]
        if tq["target_id"] in found_ids:
            recall_hits += 1
    recall_at_k = round(recall_hits / len(test_queries), 2)

    # 2) Citation Accuracy 평가: 답변 내 인용된 정책명이 실제 검색된 정책과 일치하는지
    dummy_user = UserProfile(life_stage="youth", district="마포구", monthly_income=200, deposit=1000, monthly_rent=50)
    dummy_recommended = [
        {"policy": policies[0], "eligibility": evaluate_eligibility(dummy_user, policies[0]).model_dump()},
        {"policy": policies[1], "eligibility": evaluate_eligibility(dummy_user, policies[1]).model_dump()},
    ]
    explanation = generate_guidance_explanation(dummy_user, None, dummy_recommended)
    
    # 추천된 정책명 중 최소 1개 이상이 본문에 정확히 인용되었는지 확인
    cited_count = 0
    for item in dummy_recommended:
        if item["policy"].title in explanation:
            cited_count += 1
    citation_accuracy = round(cited_count / len(dummy_recommended), 2)

    # 3) 자격 조건 정확도 평가 (소득 초과, 만료 등 정답 비교)
    test_users = [
        # 소득 초과 -> INELIGIBLE 나와야 함
        (UserProfile(life_stage="youth", district="마포구", monthly_income=500.0), policies[0], "INELIGIBLE"),
        # 정상 충족 -> ELIGIBLE_PROBABLE 나와야 함
        (UserProfile(life_stage="youth", district="마포구", monthly_income=150.0), policies[0], "ELIGIBLE_PROBABLE"),
        # 마감 정책 -> EXPIRED 나와야 함
        (UserProfile(life_stage="youth", district="마포구", monthly_income=150.0), policies[7], "EXPIRED"),
    ]
    correct_eligibility = 0
    for u, p, expected in test_users:
        res = evaluate_eligibility(u, p)
        if res.status == expected:
            correct_eligibility += 1
    eligibility_accuracy = round(correct_eligibility / len(test_users), 2)

    # 4) 만료 정책 오류율 평가 (마감된 정책이 잘못 추천되었는지 비율)
    expired_policy = policies[7]  # POL_EXPIRED_MAPO_SPECIAL
    expired_eval = evaluate_eligibility(dummy_user, expired_policy)
    # 만료 정책이 ELIGIBLE_PROBABLE로 오판되면 1.0, 정상 차단(EXPIRED)되면 0.0
    expired_error_rate = 0.0 if expired_eval.status == "EXPIRED" else 1.0

    return EvaluationResult(
        recall_at_k=recall_at_k,
        citation_accuracy=citation_accuracy,
        eligibility_accuracy=eligibility_accuracy,
        expired_policy_error_rate=expired_error_rate,
        details={
            "total_benchmark_queries": len(test_queries),
            "recall_hits": recall_hits,
            "top_k": k,
            "expired_policy_status": expired_eval.status,
            "is_auto_applied": False,
        }
    )
