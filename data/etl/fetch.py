"""1단계: 공공데이터 API에서 데이터를 받아 온다.

- 전월세 4종: XML 응답 → fetch_month()
- 법정동코드: JSON 응답 → fetch_seoul_districts()
- 회계감사보고서: JSON 응답 → fetch_audit()
"""
import time
import xml.etree.ElementTree as ET

import requests

from data.etl.config import AUDIT, ROWS_PER_PAGE, SERVICE_KEY, STAN_REGIN


def _need_key():
    if not SERVICE_KEY:
        raise RuntimeError("data/.env 에 DATA_GO_KR_KEY 를 넣어 주세요.")


def as_list(value):
    """API가 1건이면 딕셔너리, 여러 건이면 리스트를 준다. 항상 리스트로 맞춘다."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def parse_xml(xml_text):
    """XML 문자열에서 <item> 목록을 꺼내 딕셔너리 리스트로 바꾼다.

    예) <item><deposit>10,000</deposit></item> → [{"deposit": "10,000"}]
    """
    root = ET.fromstring(xml_text)

    # resultCode 가 "000" 또는 "00" 이 아니면 인증키 오류 등 실패 응답이다.
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
    """한 자치구의 한 달치 전월세 거래를 모두 가져온다. (여러 페이지면 반복 호출)"""
    _need_key()

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


def fetch_seoul_districts():
    """법정동코드 API에서 서울 25개 자치구(코드 5자리 + 구 이름)를 가져온다.

    응답에는 구와 동이 섞여 있다.
    - 구: umd_cd == "000" 이고 sgg_cd != "000"  (예: 서울특별시 마포구)
    - 동: umd_cd 가 "000" 이 아님                 (예: 서울특별시 마포구 상암동)
    실거래가 API는 구 코드 5자리(region_cd 앞 5자리)를 쓴다.
    """
    _need_key()

    rows = []
    page = 1
    while True:
        params = {
            "serviceKey": SERVICE_KEY,
            "pageNo": page,
            "numOfRows": ROWS_PER_PAGE,
            "type": "json",
            "locatadd_nm": "서울특별시",
        }
        response = requests.get(STAN_REGIN["url"], params=params, timeout=20)
        response.raise_for_status()
        body = response.json().get("StanReginCd") or []

        page_rows = []
        total_count = 0
        for part in body:
            if "head" in part:
                for item in part["head"]:
                    if "totalCount" in item:
                        total_count = int(item["totalCount"])
            if "row" in part:
                page_rows = as_list(part["row"])

        rows.extend(page_rows)
        if len(rows) >= total_count or not page_rows:
            break
        page += 1
        time.sleep(0.1)

    districts = {}
    for row in rows:
        # 서울특별시 자체(sgg_cd=000)와 동(umd_cd!=000)은 뺀다.
        if row.get("sido_cd") != "11":
            continue
        if row.get("umd_cd") != "000" or row.get("sgg_cd") == "000":
            continue
        code = str(row.get("region_cd", ""))[:5]
        name = (row.get("locallow_nm") or "").strip()
        if code and name.endswith("구"):
            districts[code] = name

    if len(districts) < 20:
        raise RuntimeError(f"서울 자치구를 충분히 못 받았습니다. ({len(districts)}개)")
    return districts


def fetch_audit(district_code):
    """한 자치구의 아파트 회계감사보고서 목록을 모두 가져온다."""
    _need_key()

    all_items = []
    page = 1
    while True:
        params = {
            "serviceKey": SERVICE_KEY,
            "pageNo": page,
            "numOfRows": ROWS_PER_PAGE,
            "bjdCode": district_code,  # 자치구 코드 5자리
        }
        response = requests.get(AUDIT["url"], params=params, timeout=20)
        response.raise_for_status()
        body = response.json().get("response", {})

        header = body.get("header") or {}
        result_code = str(header.get("resultCode", ""))
        if result_code not in ("00", "000"):
            raise RuntimeError(f"회계감사 API 오류 {result_code}: {header.get('resultMsg')}")

        inner = body.get("body") or {}
        items = as_list(inner.get("items"))
        # items 가 {"item": [...]} 형태인 경우도 있다.
        if items and isinstance(items[0], dict) and "kaptCode" not in items[0] and "item" in items[0]:
            items = as_list(items[0]["item"])

        all_items.extend(items)
        total_count = int(inner.get("totalCount") or 0)
        if len(all_items) >= total_count or not items:
            break
        page += 1
        time.sleep(0.1)

    return all_items
