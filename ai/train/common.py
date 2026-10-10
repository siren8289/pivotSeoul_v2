"""학습 스크립트가 같이 쓰는 함수."""
import json
from pathlib import Path

import pandas as pd

from ai.src.features import FEATURE_COLUMNS, TARGET_COLUMN

ROOT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
MODELS_DIR = ROOT_DIR / "ai" / "models"


def load_rent_data():
    """data 파이프라인이 만든 전처리 결과를 읽는다."""
    path = PROCESSED_DIR / "rent_clean.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} 가 없습니다. 먼저 `python -m data.etl.run` 을 실행하세요.")
    df = pd.read_csv(path)
    return df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN])


def save_district_stats():
    """자치구 통계 CSV를 AI 서버가 읽을 JSON으로 복사한다. (Docker 이미지에 models/만 넣기 위해)"""
    stats = pd.read_csv(PROCESSED_DIR / "district_stats.csv")
    stats = stats.astype(object).where(stats.notna(), None)  # NaN → null
    rows = stats.to_dict(orient="records")
    (MODELS_DIR / "district_stats.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8",
    )
