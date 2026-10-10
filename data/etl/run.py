"""데이터 파이프라인 실행: 수집 → 전처리 → 저장

사용법 (저장소 루트에서)
    python -m data.etl.run --months 2

사용하는 공공데이터 API 6개
  1. 국토부 아파트 전월세        → 학습 데이터 (apartment)
  2. 국토부 연립다세대 전월세    → 학습 데이터 (villa)
  3. 국토부 오피스텔 전월세      → 학습 데이터 (officetel)
  4. 국토부 단독/다가구 전월세   → 학습 데이터 (house)
  5. 행정안전부 법정동코드       → 서울 25개 구 코드
  6. 국토부 회계감사보고서       → 구별 관리 투명도
"""
import argparse
import json
from datetime import date

import pandas as pd

from data.etl.config import AUDIT, FALLBACK_DISTRICTS, PROCESSED_DIR, RENT_APIS, STAN_REGIN
from data.etl.fetch import fetch_audit, fetch_month, fetch_seoul_districts
from data.etl.load import save_processed, save_raw
from data.etl.transform import clean_audit, clean_rent, make_district_stats, remove_outliers


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


def collect_rent(api_id, months, districts):
    """전월세 API 하나에 대해 25개 구 × 여러 달을 모두 모은다."""
    api = RENT_APIS[api_id]
    rows = []
    for year_month in months:
        for code, name in districts.items():
            items = fetch_month(api["url"], code, year_month)
            rows.extend(items)
            print(f"  {api['name']} {year_month} {name}: {len(items)}건")
    return rows


def collect_audit(districts):
    """25개 구의 회계감사보고서 목록을 모은다."""
    rows = []
    for code, name in districts.items():
        items = fetch_audit(code)
        for item in items:
            item["district_code"] = code
        rows.extend(items)
        print(f"  {AUDIT['name']} {name}: {len(items)}건")
    return rows


def save_districts(districts):
    """구 코드 표를 CSV로 저장하고, AI 서버가 읽을 수 있게 돌려준다."""
    table = pd.DataFrame(
        [{"district_code": code, "district": name} for code, name in sorted(districts.items())]
    )
    path = save_processed(table, "seoul_districts")
    print("  ", path, f"({len(table)}개 구)")
    return table


def save_stats_json(stats):
    """자치구 통계를 AI 서버(models/)가 바로 읽도록 JSON으로도 저장한다."""
    models_dir = PROCESSED_DIR.parent.parent / "ai" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    clean = stats.astype(object).where(stats.notna(), None)
    rows = clean.to_dict(orient="records")
    path = models_dir / "district_stats.json"
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print("  ", path)


def load_or_collect_rent(months, districts, skip_rent):
    """전월세를 새로 받거나, 이미 있는 rent_clean.csv 를 읽는다."""
    saved = PROCESSED_DIR / "rent_clean.csv"
    if skip_rent and saved.exists():
        print("[2/4] 전월세: 이미 있는 rent_clean.csv 를 사용합니다")
        return pd.read_csv(saved)

    raw_rent = {}
    for api_id in RENT_APIS:
        print(f"[2/4] 수집: {RENT_APIS[api_id]['name']}")
        raw_rent[api_id] = collect_rent(api_id, months, districts)
        save_raw(raw_rent[api_id], api_id)

    rent_tables = []
    for api_id, api in RENT_APIS.items():
        table = clean_rent(raw_rent[api_id], api["house_type"], districts)
        print(f"  {api['name']}: 원본 {len(raw_rent[api_id])}건 → 정제 {len(table)}건")
        rent_tables.append(table)

    rent = pd.concat(rent_tables, ignore_index=True)
    return remove_outliers(rent, "monthly_cost", "house_type")


def run(months_count, skip_rent=False):
    months = recent_months(months_count)
    print(f"수집 기간: {months[-1]} ~ {months[0]}")

    # 1) 법정동코드 → 서울 25개 구
    print(f"[1/4] 수집: {STAN_REGIN['name']}")
    try:
        districts = fetch_seoul_districts()
        print(f"  서울 자치구 {len(districts)}개")
    except Exception as error:
        print(f"  법정동코드 API 실패, 기본 구 목록을 사용합니다: {error}")
        districts = dict(FALLBACK_DISTRICTS)
    save_raw([{"district_code": c, "district": n} for c, n in districts.items()], "seoul_districts")

    # 2) 전월세 4종 (또는 저장된 CSV)
    rent = load_or_collect_rent(months, districts, skip_rent)

    # 3) 회계감사보고서
    print(f"[3/4] 수집: {AUDIT['name']}")
    raw_audit = collect_audit(districts)
    save_raw(raw_audit, "apt_audit")

    # 4) 전처리 + 저장
    print("[4/4] 전처리·저장")
    audit = clean_audit(raw_audit, districts)
    stats = make_district_stats(rent, audit)

    save_districts(districts)
    print("  ", save_processed(rent, "rent_clean"), f"({len(rent)}건)")
    print("  ", save_processed(audit, "apt_audit_clean"), f"({len(audit)}건)")
    print("  ", save_processed(stats, "district_stats"), f"({len(stats)}건)")
    save_stats_json(stats)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="서울 전월세·법정동·회계감사 수집 (공공데이터 API 6종)")
    parser.add_argument("--months", type=int, default=2, help="최근 몇 개월을 모을지 (기본 2)")
    parser.add_argument("--skip-rent", action="store_true", help="전월세는 이미 있는 CSV를 쓰고 법정동·회계감사만 받는다")
    args = parser.parse_args()
    run(args.months, skip_rent=args.skip_rent)
