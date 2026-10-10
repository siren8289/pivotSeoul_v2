"""3단계: 결과를 CSV 파일로 저장한다."""
import pandas as pd

from data.etl.config import PROCESSED_DIR, RAW_DIR


def save_raw(rows, name):
    """API 원본을 그대로 저장한다. (문제가 생기면 원본부터 다시 확인할 수 있게)"""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{name}.csv"
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")
    return path


def save_processed(df, name):
    """전처리된 표를 저장한다. AI 학습은 이 파일을 읽는다."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / f"{name}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path
