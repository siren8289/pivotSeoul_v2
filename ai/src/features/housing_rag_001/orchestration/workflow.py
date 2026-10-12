"""LangGraph 기반 정책 오케스트레이션 워크플로우입니다.

정책 유형 분기 → 문서 검색 → 조건 검증 → 답변 생성 단계로 실행됩니다.
langgraph 패키지가 설치된 환경에서는 StateGraph를 컴파일하여 실행하고,
미설치된 환경에서는 동일한 상태 전이 흐름을 제공하는 경량 워크플로우 엔진으로 안전하게 동작합니다.
"""
from typing import Dict, Any, List, Optional
from src.features.housing_rag_001.schemas import (
    UserProfile,
    PolicyChunk,
    PolicyDocument,
    SearchResultItem,
    EligibilityResult,
)
from src.features.housing_rag_001.policy_knowledge.service import (
    get_default_policies,
    build_knowledge_base,
    get_policy_by_id,
)
from src.features.housing_rag_001.policy_search.service import search_policies
from src.features.housing_rag_001.eligibility_check.service import evaluate_eligibility
from src.features.housing_rag_001.housing_guidance.service import (
    compute_user_rir_info,
    generate_guidance_explanation,
    extract_citations,
)


def is_langgraph_installed() -> bool:
    """시스템에 langgraph 패키지가 설치되어 있는지 확인합니다."""
    try:
        import langgraph  # noqa: F401
        return True
    except ImportError:
        return False


# 1단계: 사용자 프로필 분석 및 정책 유형 분기 노드
def node_branch_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """사용자의 생애 단계, 소득, 질문 내용을 바탕으로 검색할 정책 의도와 쿼리를 결정합니다."""
    user: UserProfile = state["user"]
    query = state.get("query") or ""

    # 질문이 비어 있으면 사용자 맞춤형 기본 검색 질의를 생성
    if not query.strip():
        if user.life_stage == "youth":
            if user.monthly_rent > 0:
                intent = "청년 월세 지원 및 주거비 경감"
                search_query = "청년 월세 지원 보증금 대출"
            else:
                intent = "청년 전세 보증금 대출 및 공공임대"
                search_query = "청년 전세자금대출 보증금 지원 장기안심주택"
        elif user.life_stage == "family":
            intent = "신혼부부 및 가족 공공임대 및 대출 지원"
            search_query = "신혼부부 매입임대 장기안심주택 전세대출"
        else:
            intent = "취약계층 및 고령자 주거 바우처 지원"
            search_query = "주택 바우처 주거비 보조 장기안심"
    else:
        intent = "사용자 직접 문의"
        search_query = query

    state["intent_category"] = intent
    state["search_query"] = search_query
    return state


# 2단계: 하이브리드 정책 문서 검색 노드
def node_retrieve_documents(state: Dict[str, Any]) -> Dict[str, Any]:
    """지식 베이스에서 하이브리드 검색과 리랭킹을 통해 관련 정책 문서를 가져옵니다."""
    user: UserProfile = state["user"]
    search_query = state.get("search_query", "")
    chunks: List[PolicyChunk] = state.get("chunks") or build_knowledge_base()

    # 하이브리드 검색 및 사용자 맞춤 리랭킹
    search_results = search_policies(
        query=search_query,
        chunks=chunks,
        district=user.district,
        life_stage=user.life_stage,
        top_k=4,
    )

    state["search_results"] = search_results

    # 검색된 청크의 원본 정책 문서들 매핑
    all_policies = state.get("policies") or get_default_policies()
    retrieved_policies: List[PolicyDocument] = []
    seen_ids = set()

    for item in search_results:
        if item.policy_id not in seen_ids:
            seen_ids.add(item.policy_id)
            policy = get_policy_by_id(item.policy_id, all_policies)
            if policy:
                retrieved_policies.append(policy)

    state["retrieved_policies"] = retrieved_policies
    return state


# 3단계: 정책 자격 조건 검증 노드
def node_verify_eligibility(state: Dict[str, Any]) -> Dict[str, Any]:
    """검색된 각 정책에 대해 사용자의 자격 조건(지역, 소득, 생애단계, 기간)을 모의 검증합니다."""
    user: UserProfile = state["user"]
    retrieved_policies: List[PolicyDocument] = state.get("retrieved_policies", [])

    recommended_list: List[Dict[str, Any]] = []
    for policy in retrieved_policies:
        eligibility = evaluate_eligibility(user, policy)
        recommended_list.append({
            "policy": policy,
            "eligibility": eligibility.model_dump(),
        })

    # 신청 가능성(ELIGIBLE_PROBABLE)이 높은 정책을 앞쪽으로 배치
    priority_order = {"ELIGIBLE_PROBABLE": 0, "CONDITIONAL": 1, "INELIGIBLE": 2, "EXPIRED": 3}
    recommended_list.sort(key=lambda x: priority_order.get(x["eligibility"]["status"], 9))

    state["recommended_policies"] = recommended_list
    return state


# 4단계: RIR 연계 최종 가이던스 및 인용 생성 노드
def node_generate_guidance(state: Dict[str, Any]) -> Dict[str, Any]:
    """RIR 주거비 진단과 검증된 정책 결과를 결합하여 최종 안내 문장과 출처 인용을 생성합니다."""
    user: UserProfile = state["user"]
    recommended_list = state.get("recommended_policies", [])

    # RIR 계산 포함 여부 확인
    rir_info = None
    if state.get("include_rir_diagnosis", True):
        rir_info = compute_user_rir_info(user)

    explanation = generate_guidance_explanation(
        user=user,
        rir_info=rir_info,
        recommended_policies=recommended_list,
    )
    citations = extract_citations(recommended_list)

    state["rir_analysis"] = rir_info
    state["explanation"] = explanation
    state["citations"] = citations
    return state


def run_orchestration_workflow(
    user: UserProfile,
    query: Optional[str] = None,
    include_rir_diagnosis: bool = True,
    chunks: Optional[List[PolicyChunk]] = None,
    policies: Optional[List[PolicyDocument]] = None,
) -> Dict[str, Any]:
    """LangGraph 기반 워크플로우를 실행하여 최종 RAG 가이던스 결과를 도출합니다.
    
    1. LangGraph 설치 시 StateGraph 워크플로우 그래프 컴파일 및 호출
    2. 미설치 시 내장 경량 상태 그래프 엔진으로 동일 노드 순차 실행
    """
    initial_state: Dict[str, Any] = {
        "user": user,
        "query": query or "",
        "include_rir_diagnosis": include_rir_diagnosis,
        "chunks": chunks,
        "policies": policies,
        "intent_category": "",
        "search_query": "",
        "search_results": [],
        "retrieved_policies": [],
        "recommended_policies": [],
        "rir_analysis": None,
        "explanation": "",
        "citations": [],
    }

    # LangGraph가 사용 가능한 경우 StateGraph 활용
    if is_langgraph_installed():
        try:
            from langgraph.graph import StateGraph, END  # type: ignore

            graph = StateGraph(dict)
            graph.add_node("branch_intent", node_branch_intent)
            graph.add_node("retrieve_documents", node_retrieve_documents)
            graph.add_node("verify_eligibility", node_verify_eligibility)
            graph.add_node("generate_guidance", node_generate_guidance)

            graph.set_entry_point("branch_intent")
            graph.add_edge("branch_intent", "retrieve_documents")
            graph.add_edge("retrieve_documents", "verify_eligibility")
            graph.add_edge("verify_eligibility", "generate_guidance")
            graph.add_edge("generate_guidance", END)

            app = graph.compile()
            return app.invoke(initial_state)
        except Exception:
            # LangGraph 실행 중 오류 발생 시 안전하게 순차 실행으로 폴백
            pass

    # 경량 내장 워크플로우 엔진 실행
    state = initial_state
    state = node_branch_intent(state)
    state = node_retrieve_documents(state)
    state = node_verify_eligibility(state)
    state = node_generate_guidance(state)
    return state
