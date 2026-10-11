"""ML·DL 모델이 함께 쓰는 입력 컬럼 정의.

학습할 때와 예측할 때 컬럼 이름·순서가 같아야 하므로 한 파일에 모아 둔다.
"""
import pandas as pd

# 글자로 된 값(범주형) → 원-핫 인코딩
CATEGORY_COLUMNS = ["district", "house_type"]
# 숫자로 된 값(수치형) → 그대로 쓰거나 표준화
NUMBER_COLUMNS = ["area_m2", "building_age", "floor"]

FEATURE_COLUMNS = CATEGORY_COLUMNS + NUMBER_COLUMNS
TARGET_COLUMN = "monthly_cost"  # 예측할 값: 월 환산 주거비(만원)


def make_input_frame(district, house_type, area_m2, building_age, floor):
    """사용자 입력 1건을 모델 입력용 표(1행)로 만든다."""
    return pd.DataFrame([{
        "district": district,
        "house_type": house_type,
        "area_m2": area_m2,
        "building_age": building_age,
        "floor": floor,
    }])
