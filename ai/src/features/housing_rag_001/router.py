"""RAG 기반 주거 지원 정책 검색 및 가이던스를 제공하는 전용 FastAPI 라우터입니다.

하네스 런타임(개인정보 마스킹, 권한 검사, 입력 검증, 추적)과 워크플로우를 연계합니다.
"""
import time
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from src.features.housing_rag_001.schemas import (
    GuidanceRequest,
    GuidanceResponse,
    SearchRequest,
    SearchResultItem,
    EligibilityResult,
    EvaluationResult,
    UserProfile,
    PolicyDocument,
)
from src.features.housing_rag_001.policy_knowledge.service import (
    get_default_policies,
    build_knowledge_base,
    get_policy_by_id,
)
from src.features.housing_rag_001.policy_search.service import search_policies
from src.features.housing_rag_001.eligibility_check.service import evaluate_eligibility
from src.features.housing_rag_001.orchestration.workflow import run_orchestration_workflow
from src.features.housing_rag_001.harness.runtime import (
    mask_pii,
    check_tool_permission,
    validate_user_input,
    track_execution,
    evaluate_rag_system,
)

router = APIRouter(prefix="/api/v1/housing-rag", tags=["Housing Policy RAG"])

# 지식 베이스 메모리 캐싱 (최초 1회 로드)
_cached_policies: List[PolicyDocument] = []
_cached_chunks = []


def get_or_init_knowledge_base():
    """지식 베이스 청크와 정책 목록을 메모리에 준비합니다."""
    global _cached_policies, _cached_chunks
    if not _cached_policies:
        _cached_policies = get_default_policies()
        _cached_chunks = build_knowledge_base(_cached_policies)
    return _cached_policies, _cached_chunks


@router.get("/policies", response_model=List[PolicyDocument])
def list_policies():
    """등록된 전체 주거 정책 및 공공주택 공고 목록을 조회합니다."""
    policies, _ = get_or_init_knowledge_base()
    return policies


@router.post("/search", response_model=List[SearchResultItem])
def search_policy_api(request: SearchRequest):
    """하이브리드 검색과 재정렬을 통해 관련 주거 정책을 검색합니다."""
    # 1) 도구 권한 검사
    if not check_tool_permission("SEARCH"):
        raise HTTPException(status_code=403, detail="검색 권한이 제한되었습니다.")

    # 2) 질문 내 개인정보 마스킹
    clean_query, _ = mask_pii(request.query)

    # 3) 검색 수행
    _, chunks = get_or_init_knowledge_base()
    results = search_policies(
        query=clean_query,
        chunks=chunks,
        district=request.district,
        life_stage=request.life_stage,
        top_k=request.top_k,
    )
    return results


@router.post("/check-eligibility", response_model=EligibilityResult)
def check_eligibility_api(user: UserProfile, policy_id: str):
    """특정 주거 정책에 대해 사용자의 신청 자격 가능성을 모의 판정합니다."""
    # 1) 입력값 검증
    errors = validate_user_input(user)
    if errors:
        raise HTTPException(status_code=400, detail=", ".join(errors))

    # 2) 정책 조회
    policies, _ = get_or_init_knowledge_base()
    policy = get_policy_by_id(policy_id, policies)
    if not policy:
        raise HTTPException(status_code=404, detail="해당 정책을 찾을 수 없습니다.")

    # 3) 자격 검증 (AI 임의 확정 방지 보장)
    result = evaluate_eligibility(user, policy)
    return result


@router.post("/guidance", response_model=GuidanceResponse)
def get_housing_guidance_api(request: GuidanceRequest):
    """RIR 주거비 진단과 정책 검색·자격 검증을 종합한 RAG 가이던스를 생성합니다."""
    start_time = time.time()

    # 1) 도구 권한 확인
    if not check_tool_permission("GENERATE_GUIDANCE"):
        raise HTTPException(status_code=403, detail="가이던스 생성 권한이 없습니다.")

    # 2) 입력값 검증
    validation_errors = validate_user_input(request.user)
    if validation_errors:
        raise HTTPException(status_code=400, detail=", ".join(validation_errors))

    # 3) 개인정보(PII) 마스킹 처리
    raw_query = request.query or ""
    clean_query, has_pii = mask_pii(raw_query)

    policies, chunks = get_or_init_knowledge_base()

    # 4) 오케스트레이션 워크플로우 실행 (분기 → 검색 → 검증 → 생성)
    workflow_state = run_orchestration_workflow(
        user=request.user,
        query=clean_query,
        include_rir_diagnosis=request.include_rir_diagnosis,
        chunks=chunks,
        policies=policies,
    )

    elapsed_ms = (time.time() - start_time) * 1000.0

    # 5) 하네스 실행 지표(비용, 토큰, 시간) 추적
    prompt_sample = f"{clean_query} {request.user.model_dump_json()}"
    harness_meta = track_execution(
        prompt_text=prompt_sample,
        response_text=workflow_state.get("explanation", ""),
        elapsed_ms=elapsed_ms,
        masked=has_pii,
    )

    # 6) 최종 결과 응답 생성
    return GuidanceResponse(
        user_summary=request.user.model_dump(),
        rir_analysis=workflow_state.get("rir_analysis"),
        recommended_policies=workflow_state.get("recommended_policies", []),
        explanation=workflow_state.get("explanation", ""),
        citations=workflow_state.get("citations", []),
        harness_meta=harness_meta,
        disclaimer=(
            "AI는 정책 신청 자격을 임의로 확정하거나 자동 신청하지 않습니다. "
            "본 결과는 모의 분석 결과이므로 실제 신청 시 공식 기관(SH공사, LH공사, 마이홈 등)의 공고문을 확인하세요."
        ),
    )


@router.get("/evaluation", response_model=EvaluationResult)
def get_evaluation_metrics_api():
    """RAG 시스템의 Recall@K, Citation Accuracy, 자격 정확도 등 벤치마크 지표를 반환합니다."""
    return evaluate_rag_system()
