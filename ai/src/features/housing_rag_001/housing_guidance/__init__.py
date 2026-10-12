"""RAG 기반 주거 정책 설명 및 출처 인용 서브패키지."""
from src.features.housing_rag_001.housing_guidance.service import (
    compute_user_rir_info,
    generate_guidance_explanation,
    extract_citations,
    build_fallback_explanation,
)

__all__ = [
    "compute_user_rir_info",
    "generate_guidance_explanation",
    "extract_citations",
    "build_fallback_explanation",
]
