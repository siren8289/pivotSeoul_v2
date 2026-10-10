"""1단계: 공공데이터 API에서 데이터를 받아 온다.

- 국토교통부 API 4종: XML 응답 → fetch_month()
- 서울시 전월세 API 1종: JSON 응답 → fetch_seoul_rent()
"""
import time
import xml.etree.ElementTree as ET

import requests

from data.etl.config import ROWS_PER_PAGE, SEOUL_API_KEY, SEOUL_RENT, SERVICE_KEY


def parse_xml(xml_text):
    """XML 문자열에서 <item> 목록을 꺼내 딕셔너리 리스트로 바꾼다.

    예) <item><deposit>10,000</deposit></item> → [{"deposit": "10,000"}]
    """
    root = ET.fromstring(xml_text)

    # resultCode 가 "000" 이 아니면 인증키 오류 등 실패 응답이다.
    result_code = root.findtext("header/resultCode")
    if result_code not in ("000", "00"):
        message = root.findtext("header/resultMsg")
        raise RuntimeError(f"API 오류 {result_code}: {message}")

    items = []
    for item in root.iter("item"):
        row = {}
        for child in item:
            row[child.tag] = (child.text or "").strip()
        items.append(row)

    total_count = int(root.findtext("body/totalCount") or 0)
    return items, total_count


def fetch_month(url, district_code, year_month):
    """한 자치구의 한 달치 거래를 모두 가져온다. (여러 페이지면 반복 호출)"""
    if not SERVICE_KEY:
        raise RuntimeError("data/.env 에 DATA_GO_KR_KEY 를 넣어 주세요.")

    all_items = []
    page = 1
    while True:
        params = {
            "serviceKey": SERVICE_KEY,
            "LAWD_CD": district_code,   # 자치구 코드 5자리
            "DEAL_YMD": year_month,     # 계약년월 6자리 (예: 202608)
            "pageNo": page,
            "numOfRows": ROWS_PER_PAGE,
        }
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()

        items, total_count = parse_xml(response.text)
        all_items.extend(items)

        # 받은 건수가 전체 건수 이상이면 끝
        if len(all_items) >= total_count or not items:
            break
        page += 1
        time.sleep(0.1)  # API 서버에 부담을 주지 않도록 잠깐 쉰다.

    return all_items


def fetch_seoul_rent(district_code, start_day, end_day):
    """서울시 전월세 API에서 한 자치구의 연립다세대 거래를 기간(YYYYMMDD) 안에서 모은다.

    이 API는 최신 계약일 순으로 정렬돼 있다.
    그래서 1000건씩 앞에서부터 읽다가, 시작일보다 오래된 계약이 나오면 멈춘다.
    """
    if not SEOUL_API_KEY:
        raise RuntimeError("data/.env 에 SEOUL_API_KEY 를 넣어 주세요.")

    rows = []
    # 접수연도(RCPT_YR)로 걸러야 하므로 기간에 걸친 연도를 모두 돈다. 예) 2026, 2025
    for year in range(int(end_day[:4]), int(start_day[:4]) - 1, -1):
        start = 1
        while True:
            end = start + ROWS_PER_PAGE - 1
            url = (f"{SEOUL_RENT['url']}/{SEOUL_API_KEY}/json/{SEOUL_RENT['service']}"
                   f"/{start}/{end}/{year}/{district_code}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            body = response.json().get(SEOUL_RENT["service"])
            if body is None:  # 데이터가 없으면 {"RESULT": {"CODE": "INFO-200"}} 만 온다.
                break
            page = body.get("row", [])

            for row in page:
                day = row.get("CTRT_DAY", "")
                if start_day <= day <= end_day and row.get("BLDG_USG") == SEOUL_RENT["building_use"]:
                    rows.append(row)

            # 마지막 페이지이거나, 이 페이지의 가장 오래된 계약이 시작일보다 이전이면 끝
            oldest_day = min((row.get("CTRT_DAY", "") for row in page), default="")
            if len(page) < ROWS_PER_PAGE or oldest_day < start_day:
                break
            start = end + 1
            time.sleep(0.1)

    return rows
