"""정책 문서 검색 및 재정렬(Reranking)을 담당하는 서비스입니다.

PostgreSQL pgvector 검색 쿼리 인터페이스와 함께,
로컬 벡터 코사인 유사도(Dense)와 키워드 매칭(Sparse)을 결합한 하이브리드 검색을 제공합니다.
"""
import re
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
from src.features.housing_rag_001.schemas import PolicyChunk, SearchResultItem
from src.features.housing_rag_001.policy_knowledge.service import compute_embedding


def compute_vector_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """두 임베딩 벡터 간의 코사인 유사도를 계산합니다 (0.0 ~ 1.0 범위)."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    arr_a = np.array(vec_a).reshape(1, -1)
    arr_b = np.array(vec_b).reshape(1, -1)
    sim = cosine_similarity(arr_a, arr_b)[0][0]
    # -1~1 범위를 0~1 범위로 정규화
    return float(max(0.0, min(1.0, (sim + 1.0) / 2.0)))


def compute_keyword_score(query: str, text: str) -> float:
    """질의어(query)의 주요 단어가 문서(text)에 얼마나 포함되어 있는지 어휘 일치 점수를 계산합니다."""
    query_tokens = set(re.findall(r'[가-힣a-zA-Z0-9]+', query.lower()))
    if not query_tokens:
        return 0.0
    
    text_lower = text.lower()
    matched = 0
    for token in query_tokens:
        if token in text_lower:
            matched += 1
            
    # 일치율을 0.0 ~ 1.0으로 환산
    return float(matched / len(query_tokens))


def hybrid_search(
    query: str,
    chunks: List[PolicyChunk],
    alpha: float = 0.6,
    top_k: int = 5
) -> List[SearchResultItem]:
    """벡터 검색(Dense)과 키워드 검색(Sparse)을 결합한 하이브리드 검색을 수행합니다.
    
    alpha가 1.0에 가까울수록 의미론적 벡터 검색 비중이 높고, 0.0에 가까울수록 키워드 일치 비중이 높습니다.
    """
    if not chunks:
        return []

    query_embedding = compute_embedding(query)
    results: List[SearchResultItem] = []

    for chunk in chunks:
        # 1) 벡터 유사도 점수 (Dense)
        dense_score = 0.0
        if chunk.embedding:
            dense_score = compute_vector_similarity(query_embedding, chunk.embedding)

        # 2) 키워드 매칭 점수 (Sparse)
        sparse_score = compute_keyword_score(query, f"{chunk.title} {chunk.content}")

        # 3) 가중합 하이브리드 점수
        hybrid_score = round(alpha * dense_score + (1.0 - alpha) * sparse_score, 4)

        results.append(
            SearchResultItem(
                policy_id=chunk.policy_id,
                title=chunk.title,
                content=chunk.content,
                organization=chunk.organization,
                source_url=chunk.source_url,
                dense_score=round(dense_score, 4),
                sparse_score=round(sparse_score, 4),
                hybrid_score=hybrid_score,
                final_score=hybrid_score,
                metadata=chunk.metadata,
            )
        )

    # 하이브리드 점수 높은 순으로 정렬
    results.sort(key=lambda item: item.hybrid_score, reverse=True)
    return results[:top_k]


def rerank_policies(
    items: List[SearchResultItem],
    district: Optional[str] = None,
    life_stage: Optional[str] = None,
) -> List[SearchResultItem]:
    """사용자의 거주 지역, 생애 단계, 활성 상태 메타데이터를 반영하여 검색 결과를 재정렬합니다."""
    reranked: List[SearchResultItem] = []

    for item in items:
        meta = item.metadata
        bonus = 0.0

        # 생애단계 일치 가중치
        target_stages = meta.get("target_stages", [])
        if life_stage and life_stage in target_stages:
            bonus += 0.25

        # 자치구 일치 가중치 (전국/서울전역이거나 해당 구가 명시된 경우)
        target_districts = meta.get("target_districts", [])
        if not target_districts or (district and district in target_districts):
            bonus += 0.15

        # 활성 정책 우선 (만료된 정책은 감점)
        is_active = meta.get("is_active", True)
        if not is_active:
            bonus -= 0.50

        # 최종 점수 계산
        final_score = round(max(0.0, item.hybrid_score + bonus), 4)
        
        # 정보 복사 및 최종 점수 업데이트
        updated_item = item.model_copy()
        updated_item.final_score = final_score
        reranked.append(updated_item)

    # 최종 점수 기준 내림차순 정렬
    reranked.sort(key=lambda x: x.final_score, reverse=True)
    return reranked


def generate_pgvector_sql(embedding_dim: int = 128, table_name: str = "policy_chunks") -> str:
    """PostgreSQL pgvector 확장을 사용하는 표준 유사도 검색 SQL 쿼리를 반환합니다.
    
    운영 환경에서 pgvector 확장이 활성화되면 이 쿼리를 사용할 수 있습니다.
    """
    return (
        f"SELECT chunk_id, policy_id, title, content, organization, source_url, "
        f"1 - (embedding <=> $1::vector({embedding_dim})) AS similarity "
        f"FROM {table_name} "
        f"WHERE is_active = true "
        f"ORDER BY embedding <=> $1::vector({embedding_dim}) "
        f"LIMIT $2;"
    )


def search_policies(
    query: str,
    chunks: List[PolicyChunk],
    district: Optional[str] = None,
    life_stage: Optional[str] = None,
    top_k: int = 3,
) -> List[SearchResultItem]:
    """하이브리드 검색과 메타데이터 재정렬을 거쳐 최적의 정책 검색 결과를 반환합니다."""
    # 1) 넉넉하게 후보군 2배수 추출
    candidates = hybrid_search(query=query, chunks=chunks, alpha=0.6, top_k=max(top_k * 2, 5))
    # 2) 사용자 조건에 맞춰 리랭킹
    reranked = rerank_policies(candidates, district=district, life_stage=life_stage)
    # 3) 상위 top_k개 반환
    return reranked[:top_k]
