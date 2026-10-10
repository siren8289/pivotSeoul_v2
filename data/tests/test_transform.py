"""전처리 함수 테스트. 실행: python -m pytest data/tests"""
from data.etl.fetch import parse_xml
from data.etl.transform import calc_monthly_cost, clean_rent, clean_seoul_rent, clean_trade

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


def test_clean_seoul_rent_uses_same_columns():
    rows = [{
        "CGG_CD": "11710", "RENT_AREA": 26.22, "GRFE": "17000", "RTFE": "",
        "ARCH_YR": "2014", "FLR": 3.0, "CTRT_DAY": "20260914", "BLDG_USG": "연립다세대",
    }]
    df = clean_seoul_rent(rows, "villa")
    row = df.iloc[0]
    assert row["district"] == "송파구"
    assert row["monthly_rent"] == 0          # 빈 월세 → 0 (전세)
    assert row["rent_type"] == "jeonse"
    assert row["deal_month"] == 9
    assert row["building_age"] == 12         # 2026 - 2014


def test_clean_trade_drops_cancelled():
    rows = [
        {"sggCd": "11440", "excluUseAr": "84", "dealAmount": "139,000", "cdealType": "O"},
        {"sggCd": "11440", "excluUseAr": "84", "dealAmount": "120,000", "cdealType": " "},
    ]
    df = clean_trade(rows)
    assert len(df) == 1
    assert df.iloc[0]["price"] == 120000
