"""신규 주거 지원 정책 RAG 기능(housing_rag_001)에 대한 종합 단위 및 통합 테스트입니다."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.features.housing_rag_001.schemas import UserProfile
from src.features.housing_rag_001.policy_knowledge.service import (
    get_default_policies,
    chunk_policy_document,
    compute_embedding,
    build_knowledge_base,
    get_policy_by_id,
)
from src.features.housing_rag_001.policy_search.service import (
    hybrid_search,
    rerank_policies,
    search_policies,
    generate_pgvector_sql,
)
from src.features.housing_rag_001.eligibility_check.service import (
    evaluate_eligibility,
    check_district_match,
    check_income_match,
    check_stage_match,
    check_period_active,
)
from src.features.housing_rag_001.housing_guidance.service import (
    compute_user_rir_info,
    generate_guidance_explanation,
    extract_citations,
)
from src.features.housing_rag_001.orchestration.workflow import (
    run_orchestration_workflow,
    is_langgraph_installed,
)
from src.features.housing_rag_001.harness.runtime import (
    mask_pii,
    check_tool_permission,
    validate_user_input,
    track_execution,
    evaluate_rag_system,
)
from src.features.housing_rag_001.router import router

# 테스트용 FastAPI 앱 생성 및 라우터 등록
app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_policy_knowledge_chunking_and_embedding():
    """정책 문서를 수집하고 적절한 크기로 청킹 및 임베딩할 수 있는지 검증합니다."""
    policies = get_default_policies()
    assert len(policies) >= 7

    first_policy = policies[0]
    chunks = chunk_policy_document(first_policy)
    assert len(chunks) > 0
    assert chunks[0].policy_id == first_policy.id
    assert "source_url" in chunks[0].model_dump()

    # 임베딩 생성 검증
    embedding = compute_embedding("청년 월세 지원 정책")
    assert isinstance(embedding, list)
    assert len(embedding) > 0


def test_hybrid_search_and_reranking():
    """Dense 벡터 유사도와 Sparse 키워드 매칭이 결합된 하이브리드 검색 및 리랭킹을 검증합니다."""
    policies = get_default_policies()
    chunks = build_knowledge_base(policies)

    # 청년 월세 관련 검색
    results = search_policies(
        query="청년 월세 지원",
        chunks=chunks,
        district="마포구",
        life_stage="youth",
        top_k=3,
    )
    assert len(results) <= 3
    assert len(results) > 0
    # 상위 검색 결과의 최종 점수가 정상 계산되었는지 확인
    assert results[0].final_score > 0.0

    # pgvector SQL 쿼리 생성 함수 검증
    sql = generate_pgvector_sql(embedding_dim=128)
    assert "<=>" in sql
    assert "ORDER BY" in sql


def test_eligibility_check_and_safety_rules():
    """자격 조건 검증 로직 및 '임의 확정 방지 / 자동 신청 금지' 안전 수칙을 검증합니다."""
    policies = get_default_policies()
    youth_policy = policies[0]  # 서울시 청년월세지원 (기준 중위소득 150% 이하, 만 19~39세)
    expired_policy = policies[7]  # 만료된 마포구 특별지원

    # 1) 조건 충족 사용자 검증 -> ELIGIBLE_PROBABLE
    eligible_user = UserProfile(
        life_stage="youth",
        district="마포구",
        monthly_income=200.0,
        deposit=1000.0,
        monthly_rent=50.0,
        is_homeless=True,
        age=28,
    )
    res_eligible = evaluate_eligibility(eligible_user, youth_policy)
    assert res_eligible.status == "ELIGIBLE_PROBABLE"
    assert res_eligible.auto_applied is False  # 필수: 자동 신청 차단
    assert "공식 공고문" in res_eligible.disclaimer  # 필수: 면책 고지

    # 2) 소득 초과 사용자 검증 -> INELIGIBLE
    rich_user = UserProfile(
        life_stage="youth",
        district="마포구",
        monthly_income=500.0,  # 소득 상한 250만원 초과
        deposit=1000.0,
        monthly_rent=50.0,
        is_homeless=True,
    )
    res_ineligible = evaluate_eligibility(rich_user, youth_policy)
    assert res_ineligible.status == "INELIGIBLE"
    assert res_ineligible.auto_applied is False

    # 3) 만료된 정책 검증 -> EXPIRED
    res_expired = evaluate_eligibility(eligible_user, expired_policy)
    assert res_expired.status == "EXPIRED"


def test_housing_guidance_and_citations():
    """RIR 주거비 계산과 정책 검색 근거를 결합한 설명 및 출처 인용을 검증합니다."""
    user = UserProfile(
        life_stage="youth",
        district="마포구",
        monthly_income=300.0,
        deposit=2000.0,
        monthly_rent=80.0,
    )
    rir_info = compute_user_rir_info(user)
    assert rir_info["monthly_cost"] > 0
    assert rir_info["status"] in ["stable", "warning", "danger"]

    policies = get_default_policies()
    sample_recommended = [
        {
            "policy": policies[0],
            "eligibility": evaluate_eligibility(user, policies[0]).model_dump(),
        }
    ]
    explanation = generate_guidance_explanation(user, rir_info, sample_recommended)
    assert len(explanation) > 10

    citations = extract_citations(sample_recommended)
    assert len(citations) == 1
    assert citations[0]["organization"] == "서울특별시"
    assert citations[0]["source_url"].startswith("http")


def test_orchestration_workflow():
    """LangGraph 기반 워크플로우 실행 흐름(분기 → 검색 → 검증 → 생성)을 검증합니다."""
    user = UserProfile(
        life_stage="youth",
        district="마포구",
        monthly_income=220.0,
        deposit=1000.0,
        monthly_rent=55.0,
    )
    state = run_orchestration_workflow(
        user=user,
        query="월세 부담 줄일 수 있는 서울시 지원 정책 알려줘",
        include_rir_diagnosis=True,
    )
    assert "intent_category" in state
    assert len(state["retrieved_policies"]) > 0
    assert len(state["recommended_policies"]) > 0
    assert len(state["citations"]) > 0
    assert len(state["explanation"]) > 0


def test_harness_runtime_guards():
    """개인정보 마스킹, 권한 제어, 입력 검증 등 하네스 안전 기능을 검증합니다."""
    # 1) 개인정보 마스킹
    text_with_pii = "제 전화번호는 010-1234-5678 이고 주민번호는 950101-1234567 입니다. 마포구 101동 거주중입니다."
    masked_text, has_pii = mask_pii(text_with_pii)
    assert has_pii is True
    assert "010-1234-5678" not in masked_text
    assert "950101-1234567" not in masked_text
    assert "[연락처 마스킹]" in masked_text
    assert "[주민번호 마스킹]" in masked_text

    # 2) 도구 권한 제어
    assert check_tool_permission("SEARCH") is True
    assert check_tool_permission("AUTO_APPLY") is False
    assert check_tool_permission("SUBMIT_APPLICATION") is False

    # 3) 입력값 검증 (음수 및 비정상 수치 방어)
    invalid_raw = {
        "monthly_income": -10.0,
        "deposit": -50.0,
        "age": 150,
    }
    errors = validate_user_input(invalid_raw)
    assert len(errors) >= 2
    assert any("음수" in err for err in errors)
    assert any("나이" in err for err in errors)

    # 비정상 소득(1억원 초과) 검증
    huge_user = UserProfile(
        life_stage="youth",
        district="마포구",
        monthly_income=200000.0,
    )
    huge_errors = validate_user_input(huge_user)
    assert any("비정상" in err for err in huge_errors)

    # 4) 실행 추적 (토큰, 비용)
    track_meta = track_execution(
        prompt_text="테스트 프롬프트",
        response_text="테스트 응답",
        elapsed_ms=120.5,
        masked=True,
    )
    assert track_meta["elapsed_ms"] == 120.5
    assert track_meta["auto_apply_blocked"] is True


def test_rag_benchmark_evaluation():
    """RAG 평가 지표(Recall@K, Citation Accuracy, 자격 조건 정확도, 만료 정책 오류)를 검증합니다."""
    eval_result = evaluate_rag_system()
    assert eval_result.recall_at_k >= 0.7  # 상위 3위 내 검색 재현율
    assert eval_result.citation_accuracy >= 0.5  # 인용 정확도
    assert eval_result.eligibility_accuracy == 1.0  # 자격 판정 정확도
    assert eval_result.expired_policy_error_rate == 0.0  # 만료 정책 오판정 0%


def test_router_api_endpoints():
    """FastAPI 라우터를 통한 HTTP 요청 및 응답 처리를 검증합니다."""
    # 1) 정책 목록 조회
    res_list = client.get("/api/v1/housing-rag/policies")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 7

    # 2) 정책 검색
    res_search = client.post("/api/v1/housing-rag/search", json={
        "query": "청년 월세 대출 010-9999-8888로 알려줘",
        "top_k": 3,
        "life_stage": "youth",
    })
    assert res_search.status_code == 200
    assert len(res_search.json()) <= 3

    # 3) 자격 검증
    res_check = client.post(
        "/api/v1/housing-rag/check-eligibility?policy_id=POL_SEOUL_YOUTH_RENT",
        json={
            "life_stage": "youth",
            "district": "마포구",
            "monthly_income": 200.0,
            "deposit": 1000.0,
            "monthly_rent": 50.0,
        }
    )
    assert res_check.status_code == 200
    body_check = res_check.json()
    assert body_check["status"] == "ELIGIBLE_PROBABLE"
    assert body_check["auto_applied"] is False

    # 4) 종합 RAG 가이던스
    res_guidance = client.post("/api/v1/housing-rag/guidance", json={
        "user": {
            "life_stage": "youth",
            "district": "마포구",
            "monthly_income": 250.0,
            "deposit": 2000.0,
            "monthly_rent": 60.0,
        },
        "query": "월세 부담이 너무 큰데 지원받을 정책이 있을까요?",
        "include_rir_diagnosis": True,
    })
    assert res_guidance.status_code == 200
    body_guidance = res_guidance.json()
    assert "rir_analysis" in body_guidance
    assert "explanation" in body_guidance
    assert len(body_guidance["citations"]) > 0
    assert "AI는 정책 신청 자격을 임의로 확정하거나 자동 신청하지 않습니다" in body_guidance["disclaimer"]

    # 5) 평가 지표 조회
    res_eval = client.get("/api/v1/housing-rag/evaluation")
    assert res_eval.status_code == 200
    assert res_eval.json()["expired_policy_error_rate"] == 0.0
