# Pivot Seoul — Data Engineering / Parser

> **Spring–FastAPI–PostgreSQL 사이에서 시뮬레이션 입·출력을 안정적으로 해석·검증·정규화하는 Data Engineering(Parser) 경계**

## 1. Project Overview

Pivot Seoul MVP의 DE 범위는 공공데이터 대량 수집이 아니라, 사용자가 입력한 조건과 FastAPI 계산 결과를 **같은 계약(contract)** 으로 이동·저장하는 것입니다.

```text
Onboarding/Input
→ Session
→ Run Orchestration
→ FastAPI Request (parser)
→ Result
→ PostgreSQL
→ API / QA / DA
```

### 핵심 구현

* Spring DTO ↔ FastAPI schema **payload boundary**
* district 정규화 (`normalize_district_name`)
* required field / numeric range **contract validation**
* run/session 기준 재현성 메타데이터 설계
* v1.0 외부 공공데이터 ingestion parser 확장 경계 문서화

---

## 2. MVP Parser Boundary

MVP parser는 외부 FILE/API batch가 아니라 내부 서비스 경계입니다.

```text
Spring request DTO
→ FastAPI request schema
→ FastAPI response schema
→ Spring result DTO
→ PostgreSQL result table
```

| 검증 항목 | 설명 |
| --- | --- |
| schema compatibility | Spring DTO와 FastAPI field 정합성 |
| required field | district, income/housing cost 등 계산 입력 |
| numeric range | 음수 금액·비정상 비율 방지 |
| normalize | 서울시/서울특별시 prefix 제거 후 자치구 grain 통일 |

구현 위치:

```text
de/parser/
  normalize.py   # 자치구 이름 정규화
  validate.py    # housing request contract 검증
```

런타임 RIR 엔진은 `fastapi/housing/`에 두고, DE 폴더는 **계약·정규화·검증 경계**를 역할 단위로 모아 둡니다.

---

## 3. Data Contract

| Dataset | Grain | 핵심 키 | 추적 항목 |
| --- | --- | --- | --- |
| Session | 입력 흐름 1건 | `session_id` | input schema version |
| Run | 계산 실행 1건 | `run_id`, `session_id` | status, executedAt |
| Input Snapshot | 실행 시점 입력 | `run_id` | payload hash, rule version |
| Result | 시나리오 결과 | `result_id`, `run_id` | RIR, threshold, schema version |

---

## 4. Operational Flow

1. Onboarding에서 사용자 조건 입력  
2. Spring이 Session 생성  
3. Run 생성 후 FastAPI로 request payload 전달  
4. `de/parser` 계약 기준으로 normalize/validate  
5. FastAPI가 RIR 계산  
6. Spring이 Result를 PostgreSQL에 저장  
7. API / QA / DA가 같은 `run_id`로 확인  

---

## 5. Quality Checks

```text
run key uniqueness
required input not-null
result-to-run relationship
numeric range
request/response schema compatibility
operational DB ↔ API response reconciliation
```

---

## 6. Future (v1.0) Ingestion Parser

```text
Source API/File
→ raw immutable load
→ schema validation
→ district/life-stage normalization
→ snapshot build
→ DQ/reconciliation
→ serving
```

외부 수집 실패는 simulation transaction과 분리해 기존 RIR 계산을 막지 않습니다.

---

## 7. Folder Layout

```text
de/
├── Readme.md
└── parser/
    ├── __init__.py
    ├── normalize.py
    └── validate.py
```
