"""데이터 수집 설정값을 한 곳에 모아 둔다.

- 공공데이터포털(국토교통부) API 4종 + 서울 열린데이터광장 API 1종 주소
- 서울 25개 자치구 법정동 코드(LAWD_CD 앞 5자리)
- 결과 파일을 저장할 폴더
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
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY", "")

# 국토교통부 실거래가 API 4종
# house_type 은 우리 서비스에서 쓰는 주택 유형 이름이다.
APIS = {
    "apt_rent": {
        "name": "아파트 전월세",
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcAptRent/getRTMSDataSvcAptRent",
        "house_type": "apartment",
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
    "apt_trade": {
        "name": "아파트 매매",
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade",
        "house_type": "apartment",
    },
}

# 서울 열린데이터광장 '서울시 부동산 전월세가 정보'
# 국토부 API에는 연립·다세대(빌라) 전월세가 없어서, 이 API에서 연립다세대만 골라 쓴다.
# 주소 형식: {SEOUL_RENT_URL}/{인증키}/json/tbLnOpendataRentV/{시작번호}/{끝번호}/{접수연도}/{자치구코드}
SEOUL_RENT = {
    "name": "서울시 전월세(연립다세대)",
    "url": "http://openapi.seoul.go.kr:8088",
    "service": "tbLnOpendataRentV",
    "building_use": "연립다세대",
    "house_type": "villa",
}

# 서울 25개 자치구 코드
SEOUL_DISTRICTS = {
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
