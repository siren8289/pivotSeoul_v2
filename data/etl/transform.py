"""2단계: 받아 온 원본 데이터를 학습에 쓸 수 있게 전처리한다.

전처리 순서
  1. 숫자 문자열 정리 ("10,000" → 10000, 빈칸 → NaN)
  2. 필요한 컬럼만 고르고 이름을 통일
  3. 결측치 처리 (건축년도·층이 없으면 채우기)
  4. 잘못된 값 제거 (면적 0, 해제된 거래 등)
  5. 파생 변수 만들기 (월 환산 주거비, 건물 나이)
  6. 이상치 제거 (상하위 1%)
"""
import pandas as pd

from data.etl.config import CONVERSION_RATE, SEOUL_DISTRICTS


def to_number(series):
    """'10,000' 같은 문자열을 숫자로 바꾼다. 바꿀 수 없으면 NaN."""
    cleaned = series.astype(str).str.replace(",", "").str.strip()
    return pd.to_numeric(cleaned, errors="coerce")


def calc_monthly_cost(deposit, monthly_rent):
    """월 환산 주거비(만원) = 월세 + 보증금 × 전환율 ÷ 12"""
    return monthly_rent + deposit * CONVERSION_RATE / 12


def clean_rent(rows, house_type):
    """전월세 원본(딕셔너리 리스트)을 깔끔한 표(DataFrame)로 만든다."""
    raw = pd.DataFrame(rows)
    if raw.empty:
        return pd.DataFrame()

    df = pd.DataFrame()
    df["district_code"] = raw["sggCd"].astype(str)
    df["district"] = df["district_code"].map(SEOUL_DISTRICTS)
    df["house_type"] = house_type

    # 아파트·오피스텔은 전용면적(excluUseAr), 단독/다가구는 계약면적(totalFloorAr)을 쓴다.
    area_column = "excluUseAr" if "excluUseAr" in raw else "totalFloorAr"
    df["area_m2"] = to_number(raw[area_column])

    df["deposit"] = to_number(raw["deposit"])
    df["monthly_rent"] = to_number(raw["monthlyRent"])
    df["build_year"] = to_number(raw["buildYear"])
    # 단독/다가구에는 층 정보가 없다 → 1층으로 본다.
    df["floor"] = to_number(raw["floor"]) if "floor" in raw else 1
    df["deal_year"] = to_number(raw["dealYear"])
    df["deal_month"] = to_number(raw["dealMonth"])

    # 서울이 아니거나, 필수 값이 비어 있는 행은 버린다.
    df = df.dropna(subset=["district", "area_m2", "deposit", "monthly_rent"])
    df = df[df["area_m2"] > 5]

    # 건축년도가 비어 있으면 같은 자치구의 중앙값으로 채운다.
    df["build_year"] = df["build_year"].fillna(
        df.groupby("district")["build_year"].transform("median")
    )
    df["build_year"] = df["build_year"].fillna(df["build_year"].median())

    # 지하층(음수)은 0층으로, 빈 값은 1층으로
    df["floor"] = df["floor"].fillna(1).clip(lower=0)

    # 파생 변수
    df["monthly_cost"] = calc_monthly_cost(df["deposit"], df["monthly_rent"]).round(1)
    df["building_age"] = (df["deal_year"] - df["build_year"]).clip(0, 60)
    # 월세가 0원이면 전세, 아니면 월세
    df["rent_type"] = "wolse"
    df.loc[df["monthly_rent"] == 0, "rent_type"] = "jeonse"

    return df.drop_duplicates()


def clean_seoul_rent(rows, house_type):
    """서울시 전월세 원본을 국토부 전월세와 '같은 컬럼'으로 맞춘다.

    컬럼 이름이 달라서 먼저 이름표를 바꿔 준 뒤, 위의 clean_rent()를 그대로 재사용한다.
      CGG_CD → sggCd, RENT_AREA → excluUseAr, GRFE → deposit, RTFE → monthlyRent,
      ARCH_YR → buildYear, FLR → floor, CTRT_DAY(20260914) → dealYear(2026)·dealMonth(9)
    """
    renamed = []
    for row in rows:
        day = str(row.get("CTRT_DAY", ""))
        renamed.append({
            "sggCd": row.get("CGG_CD"),
            "excluUseAr": row.get("RENT_AREA"),
            "deposit": row.get("GRFE"),
            "monthlyRent": row.get("RTFE") or "0",  # 전세는 월세 칸이 비어 있을 수 있다.
            "buildYear": row.get("ARCH_YR"),
            "floor": row.get("FLR"),
            "dealYear": day[:4],
            "dealMonth": day[4:6],
        })
    return clean_rent(renamed, house_type)


def clean_trade(rows):
    """아파트 매매 원본을 정리한다. 계약이 해제된 거래(cdealType='O')는 뺀다."""
    raw = pd.DataFrame(rows)
    if raw.empty:
        return pd.DataFrame()

    if "cdealType" in raw:
        raw = raw[raw["cdealType"].fillna("").str.strip() != "O"]

    df = pd.DataFrame()
    df["district_code"] = raw["sggCd"].astype(str)
    df["district"] = df["district_code"].map(SEOUL_DISTRICTS)
    df["area_m2"] = to_number(raw["excluUseAr"])
    df["price"] = to_number(raw["dealAmount"])  # 만원
    df = df.dropna(subset=["district", "area_m2", "price"])
    df = df[df["area_m2"] > 5]
    df["price_per_m2"] = (df["price"] / df["area_m2"]).round(1)
    return df.drop_duplicates()


def remove_outliers(df, column, group_column):
    """그룹(주택 유형)별로 상하위 1%를 이상치로 보고 제거한다."""
    kept_parts = []
    for group_name, group in df.groupby(group_column):
        low = group[column].quantile(0.01)    # 아래에서 1% 지점의 값
        high = group[column].quantile(0.99)   # 위에서 1% 지점의 값
        kept_parts.append(group[(group[column] >= low) & (group[column] <= high)])
    return pd.concat(kept_parts, ignore_index=True)


def make_district_stats(rent_df, trade_df):
    """자치구 × 주택유형별 요약 통계를 만든다. (추천 기능에서 사용)

    jeonse_ratio(전세가율) = 아파트 전세보증금(㎡당) ÷ 아파트 매매가(㎡당)
    전세가율이 80%를 넘으면 '깡통전세' 위험이 커진다고 본다.
    """
    stats = (
        rent_df.groupby(["district", "house_type"])
        .agg(
            deal_count=("monthly_cost", "size"),
            median_monthly_cost=("monthly_cost", "median"),
            median_area_m2=("area_m2", "median"),
        )
        .reset_index()
    )

    # 아파트 전세만 골라 ㎡당 보증금 중앙값을 구한다.
    jeonse = rent_df[(rent_df["house_type"] == "apartment") & (rent_df["rent_type"] == "jeonse")]
    jeonse_per_m2 = (jeonse["deposit"] / jeonse["area_m2"]).groupby(jeonse["district"]).median()
    trade_per_m2 = trade_df.groupby("district")["price_per_m2"].median()
    jeonse_ratio = (jeonse_per_m2 / trade_per_m2).round(3).rename("jeonse_ratio")

    stats = stats.merge(jeonse_ratio, left_on="district", right_index=True, how="left")
    stats["median_monthly_cost"] = stats["median_monthly_cost"].round(1)
    stats["median_area_m2"] = stats["median_area_m2"].round(1)
    return stats
