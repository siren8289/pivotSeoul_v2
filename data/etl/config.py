"""데이터 수집 설정값을 한 곳에 모아 둔다.

사용하는 공공데이터 API 6개
  1~4. 국토교통부 전월세 실거래가 (아파트 / 연립다세대 / 오피스텔 / 단독다가구)
  5. 행정안전부 법정동코드 (서울 25개 구 코드를 받아 옴)
  6. 국토교통부 회계감사보고서 (구별 아파트 관리 투명도)
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# data/ 폴더 위치. 어디서 실행해도 같은 폴더를 가리키도록 파일 기준으로 계산한다.
DATA_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = DATA_DIR / "raw"              # API 원본을 그대로 저장하는 곳
PROCESSED_DIR = DATA_DIR / "processed"  # 전처리가 끝난 CSV를 저장하는 곳

# data/.env 파일에서 인증키를 읽는다. (.env는 git에 올리지 않는다)
load_dotenv(DATA_DIR / ".env")
SERVICE_KEY = os.getenv("DATA_GO_KR_KEY", "")

# 1~4. 국토교통부 전월세 실거래가
# house_type 은 우리 서비스에서 쓰는 주택 유형 이름이다.
RENT_APIS = {
    "apt_rent": {
        "name": "아파트 전월세",
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcAptRent/getRTMSDataSvcAptRent",
        "house_type": "apartment",
    },
    "rh_rent": {
        "name": "연립다세대 전월세",
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcRHRent/getRTMSDataSvcRHRent",
        "house_type": "villa",
    },
    "offi_rent": {
        "name": "오피스텔 전월세",
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcOffiRent/getRTMSDataSvcOffiRent",
        "house_type": "officetel",
    },
    "sh_rent": {
        "name": "단독/다가구 전월세",
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcSHRent/getRTMSDataSvcSHRent",
        "house_type": "house",
    },
}

# 5. 법정동코드. locatadd_nm=서울특별시 로 서울 전체(구+동)를 받은 뒤, 구만 고른다.
STAN_REGIN = {
    "name": "법정동코드",
    "url": "https://apis.data.go.kr/1741000/StanReginCd/getStanReginCdList",
}

# 6. 회계감사보고서 목록. bjdCode 에 자치구 코드 5자리를 넣는다.
AUDIT = {
    "name": "회계감사보고서",
    "url": "https://apis.data.go.kr/1613000/AptAccnutReportService2/getAccnutReportList2",
}

# API가 잠깐 안 될 때를 위한 서울 25개 구 코드(법정동 앞 5자리).
# 실제 수집 때는 법정동코드 API 결과를 우선 사용한다.
FALLBACK_DISTRICTS = {
    "11110": "종로구", "11140": "중구", "11170": "용산구", "11200": "성동구",
    "11215": "광진구", "11230": "동대문구", "11260": "중랑구", "11290": "성북구",
    "11305": "강북구", "11320": "도봉구", "11350": "노원구", "11380": "은평구",
    "11410": "서대문구", "11440": "마포구", "11470": "양천구", "11500": "강서구",
    "11530": "구로구", "11545": "금천구", "11560": "영등포구", "11590": "동작구",
    "11620": "관악구", "11650": "서초구", "11680": "강남구", "11710": "송파구",
    "11740": "강동구",
}

# 전월세 전환율(연 5%). 보증금을 "매달 내는 돈"으로 바꿀 때 쓴다.
# 예) 보증금 1억(10,000만원) → 10,000 × 0.05 ÷ 12 ≈ 월 41.7만원
CONVERSION_RATE = 0.05

# 한 번 호출할 때 받을 최대 건수
ROWS_PER_PAGE = 1000

# 이 해부터의 회계감사를 "최근"으로 본다. (관리 투명도 계산용)
RECENT_AUDIT_YEAR = 2023
