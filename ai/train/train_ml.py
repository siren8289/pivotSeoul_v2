"""ML 학습: 랜덤포레스트로 월 환산 주거비를 예측하는 모델을 만든다.

실행 (저장소 루트에서, data 파이프라인을 먼저 돌려야 한다)
    python -m ai.train.train_ml
"""
import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from ai.src.features import CATEGORY_COLUMNS, FEATURE_COLUMNS, NUMBER_COLUMNS, TARGET_COLUMN
from ai.train.common import MODELS_DIR, load_rent_data, save_district_stats


def build_pipeline():
    # 글자 컬럼은 원-핫 인코딩, 숫자 컬럼은 그대로 통과
    preprocessor = ColumnTransformer([
        ("category", OneHotEncoder(handle_unknown="ignore"), CATEGORY_COLUMNS),
        ("number", "passthrough", NUMBER_COLUMNS),
    ])
    # 나무 100그루, 깊이 12 제한 → 모델 파일이 너무 커지지 않게
    model = RandomForestRegressor(
        n_estimators=100, max_depth=12, min_samples_leaf=5, n_jobs=-1, random_state=42,
    )
    return Pipeline([("preprocess", preprocessor), ("model", model)])


def main():
    df = load_rent_data()
    x_train, x_test, y_train, y_test = train_test_split(
        df[FEATURE_COLUMNS], df[TARGET_COLUMN], test_size=0.2, random_state=42,
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    # 평가: MAE = 평균적으로 몇 만원 틀리는지, R2 = 1에 가까울수록 좋음
    predictions = pipeline.predict(x_test)
    metrics = {
        "rows": len(df),
        "mae": round(mean_absolute_error(y_test, predictions), 2),
        "r2": round(r2_score(y_test, predictions), 4),
    }
    print("ML 평가:", metrics)

    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(pipeline, MODELS_DIR / "rent_rf.joblib", compress=3)
    (MODELS_DIR / "metrics_ml.json").write_text(json.dumps(metrics, indent=2))
    save_district_stats()
    print("저장 완료:", MODELS_DIR / "rent_rf.joblib")


if __name__ == "__main__":
    main()
