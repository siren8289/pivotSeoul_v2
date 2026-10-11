"""ML 모델: scikit-learn 랜덤포레스트로 '적정 월 주거비'를 예측한다."""
from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "rent_rf.joblib"

# 서버가 켜진 뒤 처음 한 번만 파일을 읽고, 이후에는 메모리에 있는 모델을 쓴다.
_model = None


def load_ml_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_ml(input_frame):
    """입력 표(여러 행 가능)를 받아 예측값(만원) 리스트를 돌려준다."""
    model = load_ml_model()
    predictions = model.predict(input_frame)
    return [round(float(value), 1) for value in predictions]
