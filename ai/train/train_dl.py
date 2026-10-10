"""DL 학습: PyTorch MLP로 월 환산 주거비를 예측하는 모델을 만든다.

실행 (저장소 루트에서)
    python -m ai.train.train_dl
"""
import json

import joblib
import numpy as np
import torch
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from torch import nn

from ai.src.prediction.dl_model import RentMLP
from ai.src.prediction.features import CATEGORY_COLUMNS, FEATURE_COLUMNS, NUMBER_COLUMNS, TARGET_COLUMN
from ai.train.common import MODELS_DIR, load_rent_data

EPOCHS = 30
BATCH_SIZE = 256
LEARNING_RATE = 0.001


def main():
    torch.manual_seed(42)
    df = load_rent_data()
    x_train_df, x_test_df, y_train, y_test = train_test_split(
        df[FEATURE_COLUMNS], df[TARGET_COLUMN], test_size=0.2, random_state=42,
    )

    # 신경망은 숫자 크기에 민감하다 → 숫자 컬럼은 표준화(평균 0, 표준편차 1)
    preprocessor = ColumnTransformer([
        ("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORY_COLUMNS),
        ("number", StandardScaler(), NUMBER_COLUMNS),
    ])
    x_train = preprocessor.fit_transform(x_train_df).astype(np.float32)
    x_test = preprocessor.transform(x_test_df).astype(np.float32)

    # 주거비는 값 차이가 크다(10만원~500만원) → log(1+값)으로 바꿔서 학습하면 안정적이다.
    y_train_log = np.log1p(y_train.to_numpy()).astype(np.float32)

    x_tensor = torch.from_numpy(x_train)
    y_tensor = torch.from_numpy(y_train_log).unsqueeze(1)

    model = RentMLP(input_size=x_train.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    loss_fn = nn.MSELoss()

    for epoch in range(1, EPOCHS + 1):
        model.train()
        # 매 epoch마다 순서를 섞어서 작은 묶음(batch) 단위로 학습
        order = torch.randperm(len(x_tensor))
        total_loss = 0.0
        for start in range(0, len(order), BATCH_SIZE):
            index = order[start:start + BATCH_SIZE]
            optimizer.zero_grad()
            loss = loss_fn(model(x_tensor[index]), y_tensor[index])
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(index)
        if epoch % 5 == 0:
            print(f"epoch {epoch:2d} / loss {total_loss / len(order):.4f}")

    # 평가 (원래 단위로 되돌려서 비교)
    model.eval()
    with torch.no_grad():
        predictions = np.expm1(model(torch.from_numpy(x_test)).squeeze(1).numpy())
    metrics = {
        "rows": len(df),
        "mae": round(float(mean_absolute_error(y_test, predictions)), 2),
        "r2": round(float(r2_score(y_test, predictions)), 4),
    }
    print("DL 평가:", metrics)

    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(preprocessor, MODELS_DIR / "rent_mlp_preprocessor.joblib")
    torch.save(
        {"input_size": x_train.shape[1], "model_state_dict": model.state_dict()},
        MODELS_DIR / "rent_mlp.pt",
    )
    (MODELS_DIR / "metrics_dl.json").write_text(json.dumps(metrics, indent=2))
    print("저장 완료:", MODELS_DIR / "rent_mlp.pt")


if __name__ == "__main__":
    main()
