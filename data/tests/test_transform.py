"""전처리 함수 테스트. 실행: python -m pytest data/tests"""
from data.etl.fetch import as_list, parse_xml
from data.etl.transform import (
    calc_monthly_cost,
    clean_audit,
    clean_rent,
    district_from_address,
    make_district_stats,
)

SAMPLE_XML = """<?xml version="1.0" encoding="utf-8"?>
<response><header><resultCode>000</resultCode><resultMsg>OK</resultMsg></header>
<body><items>
<item><sggCd>11440</sggCd><excluUseAr>84.94</excluUseAr><deposit>10,000</deposit>
<monthlyRent>250</monthlyRent><buildYear>2010</buildYear><floor>3</floor>
<dealYear>2026</dealYear><dealMonth>8</dealMonth></item>
</items><totalCount>1</totalCount></body></response>"""


def test_parse_xml():
    items, total = parse_xml(SAMPLE_XML)
    assert total == 1
    assert items[0]["deposit"] == "10,000"


def test_as_list():
    assert as_list(None) == []
    assert as_list({"a": 1}) == [{"a": 1}]
    assert as_list([1, 2]) == [1, 2]


def test_monthly_cost():
    # 보증금 1억 + 월세 0 → 10000 × 0.05 / 12 = 41.67
    assert round(calc_monthly_cost(10000, 0), 2) == 41.67


def test_clean_rent():
    items, _ = parse_xml(SAMPLE_XML)
    df = clean_rent(items, "apartment")
    row = df.iloc[0]
    assert row["district"] == "마포구"
    assert row["deposit"] == 10000          # 쉼표가 사라지고 숫자가 됨
    assert row["building_age"] == 16        # 2026 - 2010
    assert row["rent_type"] == "wolse"


def test_clean_villa_uses_same_columns():
    """연립다세대 API도 아파트와 같은 컬럼(excluUseAr, deposit ...)을 쓴다."""
    rows = [{
        "sggCd": "11710", "excluUseAr": "30.16", "deposit": "4,301", "monthlyRent": "10",
        "buildYear": "2023", "floor": "3", "dealYear": "2026", "dealMonth": "8",
    }]
    df = clean_rent(rows, "villa")
    row = df.iloc[0]
    assert row["district"] == "송파구"
    assert row["house_type"] == "villa"
    assert row["rent_type"] == "wolse"


def test_clean_rent_fills_missing_build_year_and_floor():
    rows = [
        {"sggCd": "11440", "totalFloorAr": "40", "deposit": "5,000", "monthlyRent": "50",
         "buildYear": "", "dealYear": "2026", "dealMonth": "8"},
        {"sggCd": "11440", "totalFloorAr": "60", "deposit": "8,000", "monthlyRent": "0",
         "buildYear": "2000", "dealYear": "2026", "dealMonth": "8"},
    ]
    df = clean_rent(rows, "house")
    assert df["build_year"].isna().sum() == 0
    assert (df["floor"] == 1).all()
    assert set(df["rent_type"]) == {"wolse", "jeonse"}


def test_district_from_address():
    assert district_from_address("서울특별시 마포구 공덕동 188-108") == "마포구"


def test_clean_audit_and_stats():
    audit_rows = [
        {"kaptAddr": "서울특별시 마포구 공덕동 1", "kaptCode": "A12102005",
         "kaptName": "마포현대", "audtYear": "2024"},
        {"kaptAddr": "서울특별시 마포구 공덕동 1", "kaptCode": "A12102005",
         "kaptName": "마포현대", "audtYear": "2023"},
        {"kaptAddr": "서울특별시 마포구 상암동 1", "kaptCode": "A12109999",
         "kaptName": "상암", "audtYear": "2018"},  # 오래된 해 → 최근 집계에서 제외
    ]
    audit = clean_audit(audit_rows)
    assert set(audit["district"]) == {"마포구"}
    assert audit["kapt_code"].nunique() == 2

    rent = clean_rent([
        {"sggCd": "11440", "excluUseAr": "59", "deposit": "10,000", "monthlyRent": "80",
         "buildYear": "2010", "floor": "5", "dealYear": "2026", "dealMonth": "8"},
    ], "apartment")
    stats = make_district_stats(rent, audit)
    # 최근(2023 이후) 단지는 마포현대 1곳만 센다
    assert int(stats.iloc[0]["audit_count"]) == 1
