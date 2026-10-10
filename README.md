# pivotSeoul v2

서울에서 **내 월세·전세가 소득에 비해 적정한지** 진단하고, **예산에 맞는 자치구**를 추천하는 서비스입니다.
공공데이터 API 6개를 모아서 전처리하고, 머신러닝·딥러닝·LLM을 모두 사용합니다.

## 메인 기능 2개

| 기능 | 하는 일 | 사용 기술 |
| --- | --- | --- |
| 1. 내 주거비 진단 | 월 주거비 ÷ 월 소득(RIR)을 계산하고, 비슷한 집의 AI 예상 시세와 비교한 뒤 쉬운 말로 설명 | 규칙 계산 + **ML** + **DL** + **LLM** |
| 2. 자치구 추천 | 같은 조건의 집을 서울 25개 구에 놓고 예상 주거비를 계산해, 소득의 30% 안에 드는 구를 추천 | **ML** + **DL** |

- RIR 30% 이하 `안정` / 40% 이하 `주의` / 40% 초과 `위험(Red Zone)`
- 월 환산 주거비 = 월세 + 보증금 × 5% ÷ 12 (전월세 전환율 5%)
- 아파트는 회계감사 단지 수(관리 투명도)를 같이 보여 줍니다.

## 폴더 구조

IF_v2 처럼 역할별로 나눴습니다. (`ai` / `front` / `back` / `data`)

```text
pivotSeoul_v2/
├── data/                  공공데이터 수집·전처리
│   ├── etl/
│   │   ├── config.py      API 주소, 자치구 코드, 설정값
│   │   ├── fetch.py       1단계: API에서 받아 오기
│   │   ├── transform.py   2단계: 전처리 (숫자 정리, 결측치, 이상치, 파생변수)
│   │   ├── load.py        3단계: CSV로 저장
│   │   └── run.py         전체 실행 (수집 → 전처리 → 저장)
│   ├── raw/               API 원본 (git 제외)
│   ├── processed/         전처리 결과 CSV
│   └── tests/
├── ai/                    AI 서버 (FastAPI, Python)
│   ├── train/             모델 학습 코드 (ML, DL)
│   ├── models/            학습된 모델 파일
│   ├── src/               서버 코드
│   │   ├── api/           FastAPI 엔드포인트
│   │   ├── prediction/    특성 생성, ML·DL 예측
│   │   ├── domain/        RIR 규칙, 자치구 통계
│   │   ├── explain/       LLM 설명 (Gemini)
│   │   └── service.py     진단·추천 흐름 조합
│   └── tests/
├── back/                  백엔드 (Spring Boot, Java)
│   └── src/main/java/com/pivotseoul/
│       ├── diagnosis/     기능 1: 진단
│       ├── recommend/     기능 2: 추천
│       ├── ai/            AI 서버 호출
│       └── global/        오류 처리, 설정
├── front/                 프론트 (React + Vite, TypeScript)
│   └── src/
│       ├── pages/         진단 입력, 진단 결과, 추천 화면
│       ├── api/           Spring 서버 호출 함수
│       └── components/    공통 선택 목록
├── compose.yaml           전체를 한 번에 실행 (Docker)
└── .env.example           환경변수 예시
```

데이터 흐름: `공공데이터 API → data(전처리) → ai(학습) → ai 서버 ← back(Spring) ← front(Vite)`

## 사용한 공공데이터 API 6개

| # | API | 용도 |
| --- | --- | --- |
| 1 | 국토교통부 아파트 전월세 실거래가 | 학습 데이터 (apartment) |
| 2 | 국토교통부 연립다세대 전월세 실거래가 | 학습 데이터 (villa) |
| 3 | 국토교통부 오피스텔 전월세 실거래가 | 학습 데이터 (officetel) |
| 4 | 국토교통부 단독/다가구 전월세 실거래가 | 학습 데이터 (house) |
| 5 | 행정안전부 법정동코드 | 서울 25개 구 코드 |
| 6 | 국토교통부 회계감사보고서 | 구별 아파트 관리 투명도 |

### 전처리 순서 (`data/etl/transform.py`)

1. 숫자 문자열 정리 (`"10,000"` → `10000`)
2. 필요한 컬럼만 고르고 이름 통일
3. 결측치 채우기 (건축년도는 같은 구의 중앙값, 층은 1층)
4. 잘못된 값 제거 (서울 밖, 면적 5㎡ 이하)
5. 파생 변수 만들기 (월 환산 주거비, 건물 나이, 전세/월세 구분)
6. 이상치 제거 (주택 유형별 상하위 1%)
7. 자치구 × 주택유형 통계 + 최근 회계감사 단지수

## AI 모델

둘 다 같은 입력(자치구, 주택유형, 면적, 건물 나이, 층)으로 "월 환산 주거비"를 예측합니다.

| 구분 | 모델 | 파일 |
| --- | --- | --- |
| ML | scikit-learn 랜덤포레스트 | `ai/src/prediction/ml_model.py`, `ai/train/train_ml.py` |
| DL | PyTorch 다층 신경망(MLP) | `ai/src/prediction/dl_model.py`, `ai/train/train_dl.py` |
| LLM | Google Gemini (키가 없으면 기본 문장) | `ai/src/explain/llm_explain.py` |

성능은 학습 후 `ai/models/metrics_ml.json`, `metrics_dl.json`에서 볼 수 있습니다. (MAE는 평균 오차(만원), R²는 1에 가까울수록 좋음)

## 실행 방법

### 0. 준비

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r data/requirements.txt -r ai/requirements.txt
pip install torch
cp data/.env.example data/.env     # 공공데이터 인증키를 채운다
cp ai/.env.example ai/.env         # (선택) Gemini 키
```

`data/.env`에 넣을 키
- `DATA_GO_KR_KEY`: 공공데이터포털(data.go.kr) 일반 인증키 (Decoding)

### 1. 데이터 수집·전처리 (저장소 루트에서)

```bash
python -m data.etl.run --months 2     # 최근 2개월 전월세 + 법정동 + 회계감사
python -m data.etl.run --skip-rent    # 전월세 CSV는 그대로 두고 법정동·회계감사만 다시 받기
```

### 2. 모델 학습

```bash
python -m ai.train.train_ml
python -m ai.train.train_dl
```

### 3. 서버 실행 (터미널 3개)

```bash
# AI 서버 (8000)
cd ai && python -m uvicorn src.api.main:app --port 8000

# 백엔드 (8080) - 로컬에서는 H2 메모리 DB를 쓴다
cd back && ./gradlew bootRun

# 프론트 (5173)
cd front && npm install && npm run dev
```

브라우저에서 http://localhost:5173 접속.

### Docker로 한 번에 실행

```bash
cp .env.example .env      # DB_PASSWORD, (선택) GEMINI_API_KEY 입력
docker compose up --build
# 또는 서버에서
bash scripts/deploy.sh
```

http://localhost 접속. 컨테이너 안에서는 front(nginx)가 `/api`를 Spring으로 넘긴다.

## CI

푸시하면 GitHub Actions가 data / ai / back / front 테스트와 `docker compose config`를 실행한다. (`.github/workflows/ci.yml`)

## API

| 메서드 | 주소 | 설명 |
| --- | --- | --- |
| POST | `/api/diagnoses` | 진단 실행 + 저장 |
| GET | `/api/diagnoses/{id}` | 진단 결과 조회 |
| GET | `/api/diagnoses` | 최근 진단 10건 |
| POST | `/api/recommendations` | 자치구 추천 |
| GET | `/api/health` | 서버 상태 확인 |

AI 서버(FastAPI)는 Spring만 호출합니다: `POST /api/v1/diagnose`, `POST /api/v1/recommend`

## 테스트

```bash
python -m pytest data/tests          # 전처리
cd ai && python -m pytest            # AI 서버
cd back && ./gradlew test            # 백엔드
cd front && npm run build            # 프론트 (타입 검사 + 빌드)
```
