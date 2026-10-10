"""DL 모델: PyTorch 다층 퍼셉트론(MLP)으로 '적정 월 주거비'를 예측한다.

입력 전처리(원-핫 인코딩, 표준화)는 scikit-learn 으로 하고,
숫자 배열이 된 입력을 PyTorch 신경망에 넣는다.
"""
from pathlib import Path

import joblib
import numpy as np
import torch
from torch import nn

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODELS_DIR / "rent_mlp.pt"
PREPROCESSOR_PATH = MODELS_DIR / "rent_mlp_preprocessor.joblib"


class RentMLP(nn.Module):
    """입력 → 64 → 32 → 1 (예측값). 학습 코드와 구조가 똑같아야 한다."""

    def __init__(self, input_size):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        return self.layers(x)


_model = None
_preprocessor = None


def load_dl_model():
    global _model, _preprocessor
    if _model is None:
        _preprocessor = joblib.load(PREPROCESSOR_PATH)
        checkpoint = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
        _model = RentMLP(input_size=checkpoint["input_size"])
        _model.load_state_dict(checkpoint["model_state_dict"])
        _model.eval()  # 예측 모드 (Dropout 끄기)
    return _model, _preprocessor


def predict_dl(input_frame):
    """입력 표를 받아 예측값(만원) 리스트를 돌려준다."""
    model, preprocessor = load_dl_model()
    x = preprocessor.transform(input_frame).astype(np.float32)

    with torch.no_grad():
        output = model(torch.from_numpy(x)).squeeze(1).numpy()

    # 학습할 때 log(1 + 값)으로 바꿔서 학습했으므로 다시 원래 단위로 되돌린다.
    predictions = np.expm1(output)
    return [round(float(value), 1) for value in predictions]
