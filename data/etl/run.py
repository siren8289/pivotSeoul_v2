"""데이터 파이프라인 실행: 수집 → 전처리 → 저장

사용법 (저장소 루트에서)
    python -m data.etl.run --months 3

사용하는 공공데이터 API 5개
  1. 국토부 아파트 전월세      → 학습 데이터 (apartment)
  2. 국토부 오피스텔 전월세    → 학습 데이터 (officetel)
  3. 국토부 단독/다가구 전월세 → 학습 데이터 (house)
  4. 서울시 전월세(연립다세대) → 학습 데이터 (villa)
  5. 국토부 아파트 매매        → 자치구별 전세가율 계산
"""
import argparse
import calendar
from datetime import date

import pandas as pd

from data.etl.config import APIS, SEOUL_DISTRICTS, SEOUL_RENT
from data.etl.fetch import fetch_month, fetch_seoul_rent
from data.etl.load import save_processed, save_raw
from data.etl.transform import (
    clean_rent,
    clean_seoul_rent,
    clean_trade,
    make_district_stats,
    remove_outliers,
)


def recent_months(count):
    """지난달부터 거꾸로 count개월의 'YYYYMM' 목록. (이번 달은 아직 신고가 덜 돼서 뺀다)"""
    today = date.today()
    year, month = today.year, today.month
    months = []
    for _ in range(count):
        month -= 1
        if month == 0:
            year, month = year - 1, 12
        months.append(f"{year}{month:02d}")
    return months


def collect(api_id, months):
    """국토부 API 하나에 대해 25개 구 × 여러 달을 모두 모은다."""
    api = APIS[api_id]
    rows = []
    for year_month in months:
        for code, name in SEOUL_DISTRICTS.items():
            items = fetch_month(api["url"], code, year_month)
            rows.extend(items)
            print(f"  {api['name']} {year_month} {name}: {len(items)}건")
    return rows


def collect_seoul(months):
    """서울시 API로 25개 구의 연립다세대 거래를 같은 기간만큼 모은다."""
    oldest, newest = months[-1], months[0]
    start_day = f"{oldest}01"
    last_day = calendar.monthrange(int(newest[:4]), int(newest[4:]))[1]
    end_day = f"{newest}{last_day:02d}"

    rows = []
    for code, name in SEOUL_DISTRICTS.items():
        items = fetch_seoul_rent(code, start_day, end_day)
        rows.extend(items)
        print(f"  {SEOUL_RENT['name']} {name}: {len(items)}건")
    return rows


def run(months_count):
    months = recent_months(months_count)
    print(f"수집 기간: {months[-1]} ~ {months[0]}")

    # 1) 수집 + 원본 저장
    raw = {}
    for api_id in APIS:
        print(f"[1/3] 수집: {APIS[api_id]['name']}")
        raw[api_id] = collect(api_id, months)
        save_raw(raw[api_id], api_id)

    print(f"[1/3] 수집: {SEOUL_RENT['name']}")
    raw["seoul_villa_rent"] = collect_seoul(months)
    save_raw(raw["seoul_villa_rent"], "seoul_villa_rent")

    # 2) 전처리
    print("[2/3] 전처리")
    rent_tables = []
    for api_id in ["apt_rent", "offi_rent", "sh_rent"]:
        table = clean_rent(raw[api_id], APIS[api_id]["house_type"])
        print(f"  {APIS[api_id]['name']}: 원본 {len(raw[api_id])}건 → 정제 {len(table)}건")
        rent_tables.append(table)

    villa = clean_seoul_rent(raw["seoul_villa_rent"], SEOUL_RENT["house_type"])
    print(f"  {SEOUL_RENT['name']}: 원본 {len(raw['seoul_villa_rent'])}건 → 정제 {len(villa)}건")
    rent_tables.append(villa)

    rent = pd.concat(rent_tables, ignore_index=True)
    rent = remove_outliers(rent, "monthly_cost", "house_type")
    trade = clean_trade(raw["apt_trade"])
    stats = make_district_stats(rent, trade)

    # 3) 저장
    print("[3/3] 저장")
    print("  ", save_processed(rent, "rent_clean"), f"({len(rent)}건)")
    print("  ", save_processed(trade, "apt_trade_clean"), f"({len(trade)}건)")
    print("  ", save_processed(stats, "district_stats"), f"({len(stats)}건)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="서울 전월세/매매 실거래가 수집 (공공데이터 API 5종)")
    parser.add_argument("--months", type=int, default=3, help="최근 몇 개월을 모을지 (기본 3)")
    args = parser.parse_args()
    run(args.months)
