"""2단계: 받아 온 원본 데이터를 학습에 쓸 수 있게 전처리한다.

전처리 순서
  1. 숫자 문자열 정리 ("10,000" → 10000, 빈칸 → NaN)
  2. 필요한 컬럼만 고르고 이름을 통일
  3. 결측치 처리 (건축년도·층이 없으면 채우기)
  4. 잘못된 값 제거 (서울 밖, 면적 5㎡ 이하)
  5. 파생 변수 만들기 (월 환산 주거비, 건물 나이, 전세/월세)
  6. 이상치 제거 (주택 유형별 상하위 1%)
  7. 자치구 통계 + 회계감사 단지 수
"""
import pandas as pd

from data.etl.config import CONVERSION_RATE, FALLBACK_DISTRICTS, RECENT_AUDIT_YEAR


def to_number(series):
    """'10,000' 같은 문자열을 숫자로 바꾼다. 바꿀 수 없으면 NaN."""
    cleaned = series.astype(str).str.replace(",", "").str.strip()
    return pd.to_numeric(cleaned, errors="coerce")


def calc_monthly_cost(deposit, monthly_rent):
    """월 환산 주거비(만원) = 월세 + 보증금 × 전환율 ÷ 12"""
    return monthly_rent + deposit * CONVERSION_RATE / 12


def district_from_address(address):
    """'서울특별시 마포구 공덕동 ...' 에서 구 이름만 꺼낸다."""
    for part in str(address).split():
        if part.endswith("구"):
            return part
    return None


def clean_rent(rows, house_type, districts=None):
    """전월세 원본(딕셔너리 리스트)을 깔끔한 표(DataFrame)로 만든다.

    아파트·연립다세대·오피스텔은 전용면적(excluUseAr)을 쓰고,
    단독/다가구는 계약면적(totalFloorAr)을 쓴다. 컬럼 이름만 다를 뿐 처리 방법은 같다.
    """
    districts = districts or FALLBACK_DISTRICTS
    raw = pd.DataFrame(rows)
    if raw.empty:
        return pd.DataFrame()

    df = pd.DataFrame()
    df["district_code"] = raw["sggCd"].astype(str)
    df["district"] = df["district_code"].map(districts)
    df["house_type"] = house_type

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


def clean_audit(rows, districts=None):
    """회계감사보고서 목록을 정리한다.

    원본 컬럼
      kaptAddr, doroJuso, kaptCode, kaptName, audtYear
    → district, kapt_code, kapt_name, audt_year
    """
    districts = districts or FALLBACK_DISTRICTS
    raw = pd.DataFrame(rows)
    if raw.empty:
        return pd.DataFrame()

    df = pd.DataFrame()
    df["kapt_code"] = raw.get("kaptCode", pd.Series(dtype=str)).astype(str)
    df["kapt_name"] = raw.get("kaptName", pd.Series(dtype=str))
    df["audt_year"] = to_number(raw.get("audtYear", pd.Series(dtype=str)))
    df["district"] = raw.get("kaptAddr", pd.Series(dtype=str)).map(district_from_address)

    # 주소에서 구를 못 찾으면 코드로 다시 붙여 본다. (수집할 때 district_code를 넣어 둔 경우)
    if "district_code" in raw:
        missing = df["district"].isna()
        df.loc[missing, "district"] = raw.loc[missing, "district_code"].astype(str).map(districts)

    df = df.dropna(subset=["district", "kapt_code", "audt_year"])
    df = df[df["kapt_code"].str.startswith("A")]
    return df.drop_duplicates()


def remove_outliers(df, column, group_column):
    """그룹(주택 유형)별로 상하위 1%를 이상치로 보고 제거한다."""
    kept_parts = []
    for group_name, group in df.groupby(group_column):
        low = group[column].quantile(0.01)    # 아래에서 1% 지점의 값
        high = group[column].quantile(0.99)   # 위에서 1% 지점의 값
        kept_parts.append(group[(group[column] >= low) & (group[column] <= high)])
    return pd.concat(kept_parts, ignore_index=True)


def make_district_stats(rent_df, audit_df):
    """자치구 × 주택유형별 요약 통계를 만든다. (추천 기능에서 사용)

    audit_count  = 최근 회계감사 보고서가 있는 아파트 단지수
                   (클수록 관리 투명도가 높다고 본다)
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
    stats["median_monthly_cost"] = stats["median_monthly_cost"].round(1)
    stats["median_area_m2"] = stats["median_area_m2"].round(1)

    if audit_df is None or audit_df.empty:
        stats["audit_count"] = pd.NA
        return stats

    recent = audit_df[audit_df["audt_year"] >= RECENT_AUDIT_YEAR]
    audit_count = recent.groupby("district")["kapt_code"].nunique().rename("audit_count")
    stats = stats.merge(audit_count, left_on="district", right_index=True, how="left")
    return stats
