"""RAG 주거 지원 정책 서비스에서 사용하는 데이터 입출력 규격(Pydantic 스키마).

초급자도 이해하기 쉽도록 직관적인 필드명과 기본값을 사용합니다.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """사용자의 기본 정보와 주거 현황을 담는 모델입니다."""
    life_stage: str = Field(default="youth", description="생애 단계 (youth: 청년, family: 신혼·가구, senior: 고령자)")
    district: str = Field(default="마포구", description="거주 또는 희망 자치구")
    monthly_income: float = Field(gt=0, description="월 소득 (만원 단위)")
    deposit: float = Field(default=0.0, ge=0, description="현재 보증금 (만원 단위)")
    monthly_rent: float = Field(default=0.0, ge=0, description="현재 월세 (만원 단위)")
    is_homeless: bool = Field(default=True, description="무주택 여부 (기본값은 무주택)")
    age: Optional[int] = Field(default=29, ge=0, le=120, description="나이 (만 나이)")


class PolicyDocument(BaseModel):
    """주거 지원 정책 원문 정보를 담는 모델입니다."""
    id: str = Field(description="정책 고유 식별자")
    title: str = Field(description="정책 또는 공고 제목")
    target_stages: List[str] = Field(description="지원 대상 생애단계 목록 (youth, family, senior 등)")
    target_districts: List[str] = Field(default_factory=list, description="지원 자치구 (빈 리스트는 서울시 전역)")
    income_limit_monthly: Optional[float] = Field(default=None, description="월 소득 상한선 (만원 단위, 없으면 제한 없음)")
    support_type: str = Field(description="지원 유형 (월세지원, 보증금대출, 공공임대, 주거비보조)")
    benefit_summary: str = Field(description="주요 지원 혜택 요약")
    application_period: str = Field(description="신청 기간 안내 (예: 상시신청, 2026.03.01~2026.03.15)")
    is_active: bool = Field(default=True, description="현재 신청 가능한 활성 정책인지 여부")
    source_url: str = Field(description="공식 출처 또는 공고문 상세 링크")
    organization: str = Field(description="주관 기관 (예: 서울특별시, SH공사, LH공사, 국토교통부)")
    content: str = Field(description="공고 상세 설명 및 지원 요건 원문")


class PolicyChunk(BaseModel):
    """검색 및 임베딩을 위해 정책 문서를 적절한 크기로 자른 청크 모델입니다."""
    chunk_id: str = Field(description="청크 식별자")
    policy_id: str = Field(description="원본 정책 식별자")
    title: str = Field(description="정책 제목")
    content: str = Field(description="청크 본문 텍스트")
    source_url: str = Field(description="공식 출처 링크")
    organization: str = Field(description="주관 기관")
    embedding: Optional[List[float]] = Field(default=None, description="텍스트 임베딩 벡터")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="검색 필터링용 메타데이터")


class SearchRequest(BaseModel):
    """정책 검색 요청 모델입니다."""
    query: str = Field(description="검색할 질문 또는 키워드")
    top_k: int = Field(default=3, ge=1, le=10, description="반환할 최대 정책 수")
    district: Optional[str] = Field(default=None, description="필터링할 자치구")
    life_stage: Optional[str] = Field(default=None, description="필터링할 생애 단계")


class SearchResultItem(BaseModel):
    """하이브리드 검색 및 재정렬을 거친 단일 정책 검색 결과입니다."""
    policy_id: str
    title: str
    content: str
    organization: str
    source_url: str
    dense_score: float = 0.0
    sparse_score: float = 0.0
    hybrid_score: float = 0.0
    final_score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EligibilityResult(BaseModel):
    """정책 자격 조건 검증 결과 모델입니다."""
    policy_id: str
    policy_title: str
    status: str = Field(description="판정 상태 (ELIGIBLE_PROBABLE: 신청가능성 높음, CONDITIONAL: 추가조건확인, INELIGIBLE: 불일치, EXPIRED: 마감)")
    reasons: List[str] = Field(default_factory=list, description="판정 이유 목록")
    matched_conditions: List[str] = Field(default_factory=list, description="충족한 조건 목록")
    unmatched_conditions: List[str] = Field(default_factory=list, description="미충족 또는 확인 필요한 조건 목록")
    disclaimer: str = Field(
        default="본 결과는 AI 모의 확인이며 실제 신청 자격을 확정하지 않습니다. 최종 자격은 주관기관의 공식 공고문을 확인해야 합니다.",
        description="임의 확정 방지 필수 안내문구"
    )
    auto_applied: bool = Field(default=False, description="자동 신청 여부 (항상 False로 유지)")


class GuidanceRequest(BaseModel):
    """RAG 기반 주거 정책 가이던스 전체 요청 모델입니다."""
    user: UserProfile
    query: Optional[str] = Field(default=None, description="사용자 질문 (생략 시 프로필 맞춤형 질문 자동 생성)")
    include_rir_diagnosis: bool = Field(default=True, description="기존 RIR 주거비 계산 포함 여부")


class GuidanceResponse(BaseModel):
    """RAG 기반 주거 정책 가이던스 전체 응답 모델입니다."""
    user_summary: Dict[str, Any] = Field(description="사용자 입력 요약")
    rir_analysis: Optional[Dict[str, Any]] = Field(default=None, description="기존 RIR 주거비 분석 결과")
    recommended_policies: List[Dict[str, Any]] = Field(description="추천 정책 및 자격 검증 결과 목록")
    explanation: str = Field(description="RIR 분석과 검색 근거를 결합한 종합 설명")
    citations: List[Dict[str, Any]] = Field(description="공식 출처 인용 목록")
    harness_meta: Dict[str, Any] = Field(default_factory=dict, description="하네스 보안/실행 추적 메타데이터")
    disclaimer: str = Field(
        default="AI는 정책 신청 자격을 임의로 확정하거나 자동 신청하지 않습니다. 지원 전 반드시 공식 공고문과 주관기관을 확인하세요.",
        description="필수 안전 고지문"
    )


class EvaluationResult(BaseModel):
    """RAG 시스템 성능 및 안전성 평가 결과 모델입니다."""
    recall_at_k: float = Field(description="상위 K개 검색 재현율")
    citation_accuracy: float = Field(description="답변 내 인용 출처 정확도")
    eligibility_accuracy: float = Field(description="자격 조건 판정 정확도")
    expired_policy_error_rate: float = Field(description="만료된 정책이 잘못 추천된 오류율")
    details: Dict[str, Any] = Field(default_factory=dict, description="세부 평가 지표")
