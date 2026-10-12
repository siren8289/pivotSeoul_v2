"""주거 지원 정책 및 공공주택 공고를 수집, 파싱, 청킹(Chunking), 임베딩(Embedding)하는 서비스입니다.

초보자도 이해하기 쉬운 함수 위주로 작성되어 있습니다.
"""
import os
import re
import numpy as np
from typing import List, Dict, Any, Optional
from src.features.housing_rag_001.schemas import PolicyDocument, PolicyChunk


def get_default_policies() -> List[PolicyDocument]:
    """서울시의 대표 주거 지원 정책 및 공공주택 공고 목록을 반환합니다.
    
    실제 서울 청년, 신혼부부, 취약계층 정책과 테스트용 만료 정책을 포함합니다.
    """
    return [
        PolicyDocument(
            id="POL_SEOUL_YOUTH_RENT",
            title="서울시 청년월세지원",
            target_stages=["youth"],
            target_districts=[],  # 서울시 전역
            income_limit_monthly=250.0,  # 기준 중위소득 150% 이하 (약 250만원 수준)
            support_type="월세지원",
            benefit_summary="월 최대 20만원 지원 (최대 12개월간 총 240만원 지원)",
            application_period="상시 신청 및 분기별 정기 접수",
            is_active=True,
            source_url="https://housing.seoul.go.kr/site/main/content/sh01_060500",
            organization="서울특별시",
            content=(
                "서울시에 주민등록을 두고 거주하는 만 19세~39세 무주택 청년 1인 가구를 대상으로 합니다. "
                "임차보증금 5,000만원 이하 및 월세 60만원 이하 건물에 월세로 거주해야 하며, "
                "기준 중위소득 150% 이하 청년에게 월 20만원 이하의 월세를 최대 12회 지원합니다."
            ),
        ),
        PolicyDocument(
            id="POL_SEOUL_YOUTH_DEPOSIT_LOAN",
            title="서울시 청년 임차보증금 이자지원",
            target_stages=["youth"],
            target_districts=[],  # 서울시 전역
            income_limit_monthly=350.0,  # 연소득 4,000만원 이하
            support_type="보증금대출",
            benefit_summary="보증금 최대 7,000만원 한도 내에서 대출이자 연 2.0% 지원",
            application_period="연중 상시 접수",
            is_active=True,
            source_url="https://housing.seoul.go.kr/site/main/content/sh01_060400",
            organization="서울특별시",
            content=(
                "서울시 관내 주택에 전월세 계약을 체결한 만 19세~39세 이하의 청년을 지원합니다. "
                "무주택 세대주 또는 세대주 예정자여야 하며, 본인 연소득 4,000만원 이하가 대상입니다. "
                "하나은행을 통해 최대 7,000만원(보증금의 90% 이내)까지 대출이자를 연 2.0% 지원합니다."
            ),
        ),
        PolicyDocument(
            id="POL_SH_LONG_TERM_SAFE",
            title="보증금지원형 장기안심주택",
            target_stages=["youth", "family", "senior"],
            target_districts=[],  # 서울시 전역
            income_limit_monthly=320.0,  # 도시근로자 월평균소득 100% 이하
            support_type="보증금대출",
            benefit_summary="전월세 보증금의 30%(최대 6,000만원) 무이자 지원",
            application_period="연중 수시 모집",
            is_active=True,
            source_url="https://www.i-sh.co.kr/main/lay2/program/S1T294C295/www/brd/m_241/view.do",
            organization="SH 서울주택도시공사",
            content=(
                "무주택 서울시민의 주거 안정을 위해 전월세 보증금의 30%(최대 6,000만원 한도)를 최장 10년간 "
                "무이자로 지원하는 SH공사의 대표 정책입니다. 도시근로자 가구당 월평균 소득 100% 이하 무주택세대구성원이 대상이며, "
                "보증금 4억 9천만원 이하 주택에 적용됩니다."
            ),
        ),
        PolicyDocument(
            id="POL_SH_YOUTH_HOUSING",
            title="역세권 청년안심주택 공공임대",
            target_stages=["youth", "family"],
            target_districts=[],  # 서울시 전역
            income_limit_monthly=300.0,
            support_type="공공임대",
            benefit_summary="주변 시세 대비 30~50% 수준의 저렴한 임대료 공급",
            application_period="연 2~3회 정기공고",
            is_active=True,
            source_url="https://youthhousing.seoul.go.kr",
            organization="서울특별시 / SH공사",
            content=(
                "대중교통 이용이 편리한 역세권 인근에 청년과 신혼부부를 위해 공급하는 임대주택입니다. "
                "만 19세~39세 무주택자로서 차량 미보유자(생계용 등 예외)를 우선 선발합니다. "
                "공공임대의 경우 주변 시세의 30~50% 수준으로 보증금과 월세 부담을 획기적으로 낮춥니다."
            ),
        ),
        PolicyDocument(
            id="POL_MOLIT_BEOTIMOK",
            title="청년 전용 버팀목 전세자금대출",
            target_stages=["youth"],
            target_districts=[],  # 전국 (서울 포함)
            income_limit_monthly=416.0,  # 연소득 5,000만원 이하 (월 약 416만원)
            support_type="보증금대출",
            benefit_summary="연 1.8%~2.7% 초저금리 최대 2억원 전세대출",
            application_period="연중 상시",
            is_active=True,
            source_url="https://nhuf.molit.go.kr/FP/FP05/FP0502/FP05020301.jsp",
            organization="국토교통부 / 주택도시기금",
            content=(
                "만 19세 이상 34세 이하의 무주택 청년 단독세대주를 위한 전세자금 대출 상품입니다. "
                "부부합산 연소득 5,000만원 이하, 순자산 3.45억원 이하인 자가 대상입니다. "
                "임차보증금 3억원 이하 주택에 대해 최대 2억원 한도로 연 1.8%~2.7% 금리를 제공합니다."
            ),
        ),
        PolicyDocument(
            id="POL_SH_NEWLYWED_LEASE",
            title="신혼부부 매입임대주택",
            target_stages=["family"],
            target_districts=[],  # 서울시 전역
            income_limit_monthly=450.0,
            support_type="공공임대",
            benefit_summary="시세 40~50% 수준의 임대료로 최장 20년 거주",
            application_period="분기별 정기 공고",
            is_active=True,
            source_url="https://www.i-sh.co.kr",
            organization="SH 서울주택도시공사",
            content=(
                "혼인 7년 이내 신혼부부 또는 예비 신혼부부, 만 6세 이하 자녀를 둔 가구를 위한 매입임대주택입니다. "
                "무주택세대구성원으로서 전년도 도시근로자 가구원수별 월평균소득 100% 이하가 대상입니다. "
                "다세대, 오피스텔 등을 SH가 매입하여 저렴하게 재임대합니다."
            ),
        ),
        PolicyDocument(
            id="POL_SEOUL_STEPPING_STONE",
            title="서울형 주택 바우처 (주거비 보조)",
            target_stages=["youth", "family", "senior"],
            target_districts=[],  # 서울시 전역
            income_limit_monthly=160.0,  # 기준 중위소득 60% 이하
            support_type="주거비보조",
            benefit_summary="1인가구 기준 월 8만원~가구원수별 차등 지급",
            application_period="주민센터 상시 신청",
            is_active=True,
            source_url="https://housing.seoul.go.kr",
            organization="서울특별시",
            content=(
                "민간월세에 거주하는 저소득 차상위 가구를 대상으로 매월 주거비를 지원하는 서울시 복지 제도입니다. "
                "기준 중위소득 60% 이하이며 전세 전환보증금 1억 1천만원 이하 주택에 거주하는 가구에 "
                "가구원 수에 따라 매월 8만원에서 10만 5천원까지 지급합니다."
            ),
        ),
        # 테스트 및 만료 평가를 위한 지난 공고 (종료됨)
        PolicyDocument(
            id="POL_EXPIRED_MAPO_SPECIAL",
            title="2025 마포구 청년 주거비 한시 특별지원 (모집마감)",
            target_stages=["youth"],
            target_districts=["마포구"],
            income_limit_monthly=200.0,
            support_type="월세지원",
            benefit_summary="월 15만원 추가 지원 (모집 종료)",
            application_period="2025.01.01 ~ 2025.02.28 (마감)",
            is_active=False,  # 마감된 정책
            source_url="https://www.mapo.go.kr",
            organization="마포구청",
            content=(
                "2025년 마포구에 거주하는 청년을 위해 한시적으로 운영되었던 지원 사업으로 현재는 접수가 종료되었습니다. "
                "마감된 정책이므로 신규 신청이 불가능합니다."
            ),
        ),
    ]


def chunk_policy_document(policy: PolicyDocument, chunk_size: int = 250, chunk_overlap: int = 50) -> List[PolicyChunk]:
    """긴 정책 문서를 검색하기 좋은 작은 단위(청크)로 나눕니다.
    
    정책 제목, 지원 내용, 자격 조건 등을 문장 단위로 분할하여 컨텍스트 손실을 줄입니다.
    """
    chunks: List[PolicyChunk] = []
    full_text = f"[{policy.title}] ({policy.organization})\n혜택: {policy.benefit_summary}\n대상: {', '.join(policy.target_stages)}\n내용: {policy.content}"
    
    # 문장 또는 온점/줄바꿈 기준으로 나눕니다.
    sentences = re.split(r'(?<=[.?!])\s+|\n+', full_text)
    current_chunk_words: List[str] = []
    current_length = 0
    chunk_index = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        sent_len = len(sentence)
        if current_length + sent_len > chunk_size and current_chunk_words:
            chunk_content = " ".join(current_chunk_words)
            chunk_id = f"{policy.id}_c{chunk_index}"
            chunks.append(
                PolicyChunk(
                    chunk_id=chunk_id,
                    policy_id=policy.id,
                    title=policy.title,
                    content=chunk_content,
                    source_url=policy.source_url,
                    organization=policy.organization,
                    metadata={
                        "target_stages": policy.target_stages,
                        "target_districts": policy.target_districts,
                        "income_limit_monthly": policy.income_limit_monthly,
                        "support_type": policy.support_type,
                        "is_active": policy.is_active,
                        "application_period": policy.application_period,
                    }
                )
            )
            chunk_index += 1
            # 오버랩을 위해 마지막 일부 단어 유지
            overlap_words = current_chunk_words[-2:] if len(current_chunk_words) >= 2 else []
            current_chunk_words = overlap_words + [sentence]
            current_length = sum(len(w) for w in current_chunk_words)
        else:
            current_chunk_words.append(sentence)
            current_length += sent_len

    if current_chunk_words:
        chunk_content = " ".join(current_chunk_words)
        chunk_id = f"{policy.id}_c{chunk_index}"
        chunks.append(
            PolicyChunk(
                chunk_id=chunk_id,
                policy_id=policy.id,
                title=policy.title,
                content=chunk_content,
                source_url=policy.source_url,
                organization=policy.organization,
                metadata={
                    "target_stages": policy.target_stages,
                    "target_districts": policy.target_districts,
                    "income_limit_monthly": policy.income_limit_monthly,
                    "support_type": policy.support_type,
                    "is_active": policy.is_active,
                    "application_period": policy.application_period,
                }
            )
        )

    return chunks


def _local_hash_embedding(text: str, dim: int = 128) -> List[float]:
    """API 키가 없거나 외부 통신이 안 될 때 사용하는 오프라인 결정론적 로컬 임베딩입니다.
    
    단어 토큰 해싱을 통해 128차원 단위 벡터를 생성하므로 scikit-learn 코사인 유사도 검색과 완벽히 호환됩니다.
    """
    vec = np.zeros(dim, dtype=np.float32)
    # 한국어/영문 단어 추출
    tokens = re.findall(r'[가-힣a-zA-Z0-9]+', text.lower())
    if not tokens:
        return vec.tolist()
    
    for token in tokens:
        # 단어 해시값을 차원 인덱스로 매핑
        h = hash(token)
        idx = abs(h) % dim
        sign = 1.0 if (h // dim) % 2 == 0 else -1.0
        vec[idx] += sign

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def compute_embedding(text: str) -> List[float]:
    """텍스트의 임베딩 벡터를 추출합니다.
    
    GEMINI_API_KEY 가 설정되어 있으면 Gemini 임베딩 모델을 호출하고,
    키가 없거나 호출 실패 시 로컬 해시 임베딩을 안전하게 반환합니다.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=10000))
            # Gemini text embedding 모델 호출
            resp = client.models.embed_content(
                model="text-embedding-004",
                contents=text,
            )
            if resp.embeddings and len(resp.embeddings) > 0:
                values = resp.embeddings[0].values
                return list(values)
        except Exception:
            # 외부 API 오류 시 조용히 로컬 임베딩 fallback
            pass

    return _local_hash_embedding(text)


def build_knowledge_base(policies: Optional[List[PolicyDocument]] = None) -> List[PolicyChunk]:
    """전체 정책 문서를 청킹하고 임베딩을 계산하여 검색 가능한 지식 베이스를 생성합니다."""
    if policies is None:
        policies = get_default_policies()

    all_chunks: List[PolicyChunk] = []
    for policy in policies:
        chunks = chunk_policy_document(policy)
        for chunk in chunks:
            chunk.embedding = compute_embedding(chunk.content)
            all_chunks.append(chunk)

    return all_chunks


def get_policy_by_id(policy_id: str, policies: Optional[List[PolicyDocument]] = None) -> Optional[PolicyDocument]:
    """정책 ID로 해당 정책의 원본 정보를 찾습니다."""
    if policies is None:
        policies = get_default_policies()
    for policy in policies:
        if policy.id == policy_id:
            return policy
    return None
