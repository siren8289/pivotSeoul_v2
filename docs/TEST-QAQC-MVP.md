# Pivot Seoul Test / QAQC 문서 (MVP)

---

## 1. 문서 정보

| 항목 | 내용 |
| --- | --- |
| 문서명 | Pivot Seoul Test / QAQC 문서 (MVP) |
| 버전 | v0.1-mvp |
| 작성일 | 2026-07-02 |
| 작성자 | Pivot Seoul QA |
| 대상 릴리즈 | MVP |
| 관련 문서 | `docs/PRD-MVP.md`, `docs/SRS-MVP.md`, `docs/SDD-MVP.md`, Flyway V1/V6, OpenAPI |

---

## 2. 문서 목적

Pivot Seoul MVP의 **3개 핵심 기능**(세션·온보딩, RIR 시뮬 실행, 결과 조회)이 SRS 수용 기준을 만족하는지 검증하기 위한 테스트·QA/QC 기준 문서다.

```
PRD-MVP → SRS-MVP → SDD-MVP → Test/QAQC-MVP → Release
```

**MVP 검증 한 줄:** 생애단계 선택 후 소득·주거비를 넣으면 RIR과 Red Zone이 정확히 계산·표시되는가?

---

## 3. QA / QC 구분

| 구분 | MVP 적용 |
| --- | --- |
| QA | PRD/SRS/SDD 정합성 리뷰, 테스트 계획·데이터 준비, P0 TC 작성 완료 여부 |
| QC | API·DB·화면 실제 실행, Pass/Fail 기록, Bug Report 등록·재검증 |
| Testing | JUnit(housing RIR), API 통합 테스트, E2E(Home→Results) |

---

## 4. 테스트 범위

### 4.1 In Scope

| 범위 ID | 테스트 대상 | MVP 설명 |
| --- | --- | --- |
| TS-001 | 기능 테스트 | F-001~F-003 정상 흐름 |
| TS-002 | API 테스트 | 3개 Endpoint 요청/응답/에러 |
| TS-003 | DB 테스트 | session, run, result, threshold 저장 |
| TS-004 | 알고리즘 테스트 | RIR·Red Zone 판정 (BR-001~005) |
| TS-005 | 예외 테스트 | 필수값 누락, 세션 없음, AI 장애 |
| TS-006 | 화면 테스트 | 5화면 플로우, Red Zone 표시 |

### 4.2 Out of Scope

| 제외 항목 | 제외 이유 | 향후 |
| --- | --- | --- |
| A/B 시나리오 | MVP 제외 | v1.0 |
| 관리자·JWT 권한 | MVP 제외 | v1.0 |
| 커리어·보육·LLM 파이프라인 | MVP 제외 | v1.1+ |
| 부하·스트레스 테스트 | MVP 초기 | v1.0 |
| 보안 침투 테스트 | 별도 점검 | 운영 전 |
| 전체 크로스브라우저 | Chrome 우선 | v1.0 |

---

## 5. 테스트 전략

| 테스트 유형 | MVP 목적 | 대상 | 수행 시점 |
| --- | --- | --- | --- |
| Unit Test | RIR 공식 검증 | `housing/rir.py`, Spring calculators | 개발 중 |
| Integration Test | API→DB 저장 | Session, Run, Result Service | 기능 완료 후 |
| API Test | 3 Endpoint 계약 | Postman / REST Assured | API 완료 후 |
| E2E Test | 사용자 5단계 플로우 | Playwright / 수동 | 통합 후 |
| Regression Test | Run 수정 후 영향 | P0 TC 전체 | 배포 전 |
| Acceptance Test | SRS TC-001~003 Pass | QA sign-off | 릴리즈 전 |

---

## 6. 테스트 환경

| 항목 | 내용 |
| --- | --- |
| Frontend | React, Vite/Next (`front/`) |
| Backend | Spring Boot 3.x, Java 17+ (`back/`) |
| AI | FastAPI `housing` 모듈 (`fastapi/housing/`) |
| Database | PostgreSQL, Flyway V1~V7 |
| Test DB | Local Docker PostgreSQL 또는 Dev |
| API Tool | Swagger `/swagger-ui.html`, curl, Postman |
| 자동화 | JUnit 5, pytest (housing), Playwright (선택) |
| 이슈 관리 | GitHub Issues |

**기동 순서 (수동/E2E 공통):**

1. PostgreSQL + Flyway migrate
2. `back`: `./gradlew bootRun` (8080)
3. `fastapi`: `uvicorn main:app` (8000)
4. `front`: `npm run dev` (3000)

---

## 7. 테스트 데이터

| 데이터 ID | 데이터명 | 값 | 용도 |
| --- | --- | --- | --- |
| TD-001 | 정상 청년 세션 | lifeStageCode=`youth`, 마포구, 소득 450만, 주거 180만 | TC-001, TC-002 stable/warning |
| TD-002 | Red Zone 세션 | 소득 500만, 주거 225만 (RIR=0.45) | TC-002 Red Zone |
| TD-003 | 경계값 warning | 소득 500만, 주거 200만 (RIR=0.40) | BR-003 경계 |
| TD-004 | stable 구간 | 소득 500만, 주거 150만 (RIR=0.30) | BR-002 |
| TD-005 | invalid 소득 | monthly_income=0 | TC-003 예외 |
| TD-006 | 없는 세션 | sessionId=999999 | TC-004 404 |

**단위:** API 요청의 `monthly_income`, `monthly_housing_cost`는 **원(₩)**. 화면 슬라이더는 만원 → `× 10,000` 변환.

**시드 의존:** `V6__mvp_seed_data.sql` — `life_stage`(YOUTH/FAMILY/SENIOR), `threshold_type`(HOUSING) 필수.

**데모 DB 적재:** Flyway 이후 `./db/load.sh` — 상세 `db/README.md`.

---

## 8. 테스트케이스 목록

| TC ID | 기능 | 테스트 항목 | 사전조건 | 우선순위 | 상태 |
| --- | --- | --- | --- | --- | --- |
| TC-001 | F-001 세션 생성 | 정상 세션·Scenario 생성 | DB 시드 완료 | P0 | Not Run |
| TC-002 | F-001 세션 생성 | lifeStageCode 누락/무효 | — | P0 | Not Run |
| TC-003 | F-002 RIR 실행 | Red Zone (RIR=0.45) | TC-001 세션 | P0 | Not Run |
| TC-004 | F-002 RIR 실행 | stable (RIR=0.30) | TC-001 세션 | P0 | Not Run |
| TC-005 | F-002 RIR 실행 | warning 경계 (RIR=0.40) | TC-001 세션 | P1 | Not Run |
| TC-006 | F-002 RIR 실행 | 소득 0 → RIR null | TC-001 세션 | P0 | Not Run |
| TC-007 | F-002 RIR 실행 | 존재하지 않는 sessionId | — | P0 | Not Run |
| TC-008 | F-002 RIR 실행 | FastAPI 다운 | AI 서버 중지 | P1 | Not Run |
| TC-009 | F-003 결과 조회 | 정상 결과·threshold | TC-003 완료 | P0 | Not Run |
| TC-010 | F-003 결과 조회 | 없는 scenarioResultId | — | P0 | Not Run |
| TC-011 | E2E | Home→Results 전체 플로우 | 3서버 기동 | P0 | Not Run |
| TC-012 | DB | Run·Result·Threshold 저장 | TC-003 완료 | P0 | Not Run |
| TC-013 | NFR | 결과 조회 응답 시간 | TC-009 | P1 | Not Run |

---

## 9. 테스트케이스 상세

### TC-001. 세션 정상 생성

| 항목 | 내용 |
| --- | --- |
| Test Case ID | TC-001 |
| 관련 요구사항 | FR-001 |
| 관련 API | POST `/api/simulation/sessions` |
| 우선순위 | P0 |
| 테스트 유형 | API / DB |
| 사전조건 | Flyway V6 시드 적용, Spring 기동 |
| 테스트 데이터 | TD-001 |

#### 테스트 절차

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | POST body: `{ "lifeStageCode": "youth", "currentDistrict": "마포구", "monthlyIncome": 4500000, "monthlyHousing": 1800000 }` | HTTP 201 |
| 2 | 응답 body 확인 | `data.sessionId`(number), `data.sessionUuid`(string), `sessionStatus`=READY |
| 3 | DB `simulation_session` 조회 | 1건, `life_stage_id` → YOUTH |
| 4 | DB `scenario` 조회 | session_id당 1건, `scenario_type`='A' |
| 5 | DB `user_condition` 조회 | `monthly_income`=4500000, `monthly_housing`=1800000 |

---

### TC-003. RIR Red Zone 실행

| 항목 | 내용 |
| --- | --- |
| Test Case ID | TC-003 |
| 관련 요구사항 | FR-003, BR-004 |
| 관련 API | POST `/api/simulation-sessions/{sessionId}/run` |
| 우선순위 | P0 |
| 테스트 유형 | API / DB / 알고리즘 |
| 사전조건 | TC-001 sessionId, FastAPI 기동 |
| 테스트 데이터 | TD-002 |

#### 테스트 절차

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | POST run: `{ "district": "마포구", "monthly_income": 5000000, "monthly_housing_cost": 2250000 }` | HTTP 200 |
| 2 | 응답 확인 | `runStatus`=COMPLETED, `rir`=0.45, `riskScore`=80 |
| 3 | `thresholdResults[0]` | `thresholdType`=HOUSING, `isRedZone`=true, `calculatedValue`=0.45 |
| 4 | `scenarioResultId` 존재 | number, null 아님 |
| 5 | DB `simulation_run` | `run_status`=COMPLETED |
| 6 | DB `threshold_result` | `is_red_zone`=true, `calculated_value`=0.45 |

---

### TC-009. 결과 조회

| 항목 | 내용 |
| --- | --- |
| Test Case ID | TC-009 |
| 관련 요구사항 | FR-004 |
| 관련 API | GET `/api/simulation/results/{scenarioResultId}` |
| 우선순위 | P0 |
| 테스트 유형 | API / 화면 |
| 사전조건 | TC-003 `scenarioResultId` |
| 테스트 데이터 | TD-002 |

#### 테스트 절차

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | GET `/api/simulation/results/{scenarioResultId}` | HTTP 200 |
| 2 | `summary.riskScore` | 80 |
| 3 | `thresholds[0].redZone` | true |
| 4 | `thresholds[0].calculatedValue` | 0.45 |
| 5 | Results 화면 진입 | Red Zone 배지, RIR 45% 게이지 표시 |

---

### TC-011. E2E 전체 플로우

| 항목 | 내용 |
| --- | --- |
| Test Case ID | TC-011 |
| 관련 요구사항 | FR-001~004, NFR-004 |
| 우선순위 | P0 |
| 테스트 유형 | E2E |
| 사전조건 | Front/Back/FastAPI/DB 모두 기동 |

#### 테스트 절차

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | `/` → "시작하기" → `/stage` | 생애단계 화면 |
| 2 | 청년기 선택 | `/onboarding` |
| 3 | 마포구, 소득 500만, 주거 225만 입력 → 실행 | `/simulation-run`, 로딩 후 COMPLETED |
| 4 | "결과 보기" | `/results` |
| 5 | 화면 확인 | Red Zone 표시, RIR 45% |

---

## 10. API 테스트

| API ID | Method | Endpoint | 요청 조건 | 기대 응답 | TC | Status |
| --- | --- | --- | --- | --- | --- | --- |
| API-001 | POST | `/api/simulation/sessions` | TD-001 body | 201, sessionId·uuid | TC-001 | Not Run |
| API-001-E1 | POST | `/api/simulation/sessions` | lifeStageCode 누락 | 400 VALIDATION_ERROR | TC-002 | Not Run |
| API-001-E2 | POST | `/api/simulation/sessions` | lifeStageCode=`invalid` | 400 | TC-002 | Not Run |
| API-002 | POST | `/api/simulation-sessions/{id}/run` | TD-002 body | 200, rir=0.45, redZone | TC-003 | Not Run |
| API-002-E1 | POST | `.../999999/run` | 유효 body | 400 세션 없음 | TC-007 | Not Run |
| API-002-E2 | POST | `.../{id}/run` | income=0 | 200, rir=null 또는 unknown | TC-006 | Not Run |
| API-002-E3 | POST | `.../{id}/run` | FastAPI down | 503 FASTAPI_UNREACHABLE | TC-008 | Not Run |
| API-003 | GET | `/api/simulation/results/{id}` | TC-003 result id | 200, thresholds 포함 | TC-009 | Not Run |
| API-003-E1 | GET | `/api/simulation/results/999999` | — | 200 placeholder 또는 404 | TC-010 | Not Run |

**curl 예시 (TC-003):**

```bash
# 1) 세션 생성
SESSION=$(curl -s -X POST http://localhost:8080/api/simulation/sessions \
  -H 'Content-Type: application/json' \
  -d '{"lifeStageCode":"youth","currentDistrict":"마포구","monthlyIncome":5000000,"monthlyHousing":2250000}' \
  | jq -r '.data.sessionId')

# 2) 실행
curl -s -X POST "http://localhost:8080/api/simulation-sessions/${SESSION}/run" \
  -H 'Content-Type: application/json' \
  -d '{"district":"마포구","monthly_income":5000000,"monthly_housing_cost":2250000}' | jq

# 3) 결과 (scenarioResultId 치환)
curl -s "http://localhost:8080/api/simulation/results/{scenarioResultId}" | jq
```

---

## 11. DB 검증

| DB TC ID | 대상 테이블 | 검증 항목 | 검증 SQL | 기대 | TC |
| --- | --- | --- | --- | --- | --- |
| DBTC-001 | life_stage | 시드 3건 | `SELECT COUNT(*) FROM life_stage;` | 3 | TC-001 |
| DBTC-002 | threshold_type | HOUSING 존재 | `SELECT * FROM threshold_type WHERE threshold_code='HOUSING';` | 1건 | TC-003 |
| DBTC-003 | simulation_session | 세션 생성 | `SELECT * FROM simulation_session WHERE session_id=?;` | 1건, READY | TC-001 |
| DBTC-004 | scenario | 단일 A | `SELECT * FROM scenario WHERE session_id=?;` | 1건, type A | TC-001 |
| DBTC-005 | simulation_run | Run 완료 | `SELECT run_status FROM simulation_run WHERE session_id=? ORDER BY simulation_run_id DESC LIMIT 1;` | COMPLETED | TC-003 |
| DBTC-006 | scenario_result | 결과 저장 | `SELECT risk_score FROM scenario_result WHERE simulation_run_id=?;` | 80 | TC-003 |
| DBTC-007 | threshold_result | Red Zone | `SELECT is_red_zone, calculated_value FROM threshold_result WHERE scenario_result_id=?;` | true, 0.45 | TC-003 |
| DBTC-008 | calculation_log | 감사 로그 | `SELECT passed_validation FROM calculation_log WHERE simulation_run_id=?;` | true | TC-003 |

---

## 12. 알고리즘 단위 테스트 (RIR)

| AT ID | 입력 (소득, 주거비) | 기대 RIR | status | is_red_zone | risk_score |
| --- | --- | --- | --- | --- | --- |
| AT-001 | 5,000,000 / 1,500,000 | 0.30 | stable | false | 20 |
| AT-002 | 5,000,000 / 2,000,000 | 0.40 | warning | false | 50 |
| AT-003 | 5,000,000 / 2,250,000 | 0.45 | danger | true | 80 |
| AT-004 | 0 / 1,000,000 | null | unknown | false | 0 |
| AT-005 | null / null | null | unknown | false | 0 |

**구현 위치:** `fastapi/housing/rir.py`  
**자동화:** pytest `test_rir.py` (추가 권장)

---

## 13. 결함/Bug Report 템플릿

| 항목 | 내용 |
| --- | --- |
| Bug ID | BUG-XXX |
| 발견일 | YYYY-MM-DD |
| 관련 TC | TC-00X |
| 심각도 | Critical / Major / Minor / Trivial |
| 우선순위 | P0 / P1 / P2 |
| 상태 | Open / Fixed / Retest / Closed |
| 환경 | Local / Dev / Staging |
| 제목 | [한 줄 요약] |
| 재현 절차 | 1. … 2. … |
| 기대 결과 | SRS/TC 기준 |
| 실제 결과 | 관측값 |
| 첨부 | 스크린샷 / curl 응답 / 로그 |

---

## 14. 결함 심각도 기준 (MVP)

| 심각도 | MVP 기준 | 예시 |
| --- | --- | --- |
| Critical | 핵심 3기능 불가 | 세션 생성 실패, Run 항상 FAILED, 결과 미표시 |
| Major | RIR/Red Zone 오판 | 0.45인데 stable 표시, DB 미저장 |
| Minor | UX·문구 | 만원/원 단위 혼동 표시, 로딩 문구 오류 |
| Trivial | 스타일 | 여백, 아이콘 |

---

## 15. 테스트 완료 기준 (MVP Release Gate)

| 기준 | 완료 조건 |
| --- | --- |
| P0 TC (TC-001~004, 006~007, 009~012) | 100% Pass |
| P1 TC | 90% 이상 Pass 또는 승인된 예외 |
| Critical Bug | 0건 |
| Major Bug | 0건 또는 PM 승인 예외 |
| API-001~003 | 정상·대표 예외 케이스 Pass |
| DBTC-001~008 | Pass |
| E2E TC-011 | Pass |
| V6 시드 | 모든 환경 적용 확인 |

---

## 16. 테스트 결과 요약

| 항목 | 수량 |
| --- | --- |
| 전체 테스트케이스 | 13 |
| Pass | 0 |
| Fail | 0 |
| Blocked | 0 |
| Not Run | 13 |
| Pass Rate | 0% |
| Open Bug | 0 |
| Critical Bug | 0 |

> 릴리즈 전 QA가 본 표를 갱신한다.

---

## 17. 요구사항 추적성

| PRD | SRS | API | TC | DBTC | 결과 |
| --- | --- | --- | --- | --- | --- |
| F-001 | FR-001, FR-002 | API-001 | TC-001, TC-002 | DBTC-003,004 | Not Run |
| F-002 | FR-003 | API-002 | TC-003~008 | DBTC-005~008 | Not Run |
| F-003 | FR-004 | API-003 | TC-009, TC-010 | DBTC-006,007 | Not Run |
| — | BR-001~005 | — | AT-001~005 | — | Not Run |
| — | NFR-001 | API-003 | TC-013 | — | Not Run |
| — | NFR-004 | — | TC-011 | — | Not Run |

---

## 18. QA 체크리스트 (릴리즈 전)

| 체크 항목 | 확인 |
| --- | --- |
| PRD/SRS/SDD-MVP와 TC가 일치하는가? | □ |
| P0 TC가 정상·예외·DB를 포함하는가? | □ |
| 테스트 데이터(TD-001~006)가 정의되었는가? | □ |
| V6 시드(life_stage, HOUSING)가 환경에 적용되었는가? | □ |
| 만원↔원 변환 테스트가 포함되었는가? | □ |
| FastAPI 장애 시나리오(TC-008)가 있는가? | □ |
| E2E 플로우(TC-011)가 정의되었는가? | □ |
| Release Gate(§15)가 합의되었는가? | □ |

---

## 19. QC 체크리스트 (실행 후)

| 체크 항목 | 확인 |
| --- | --- |
| P0 TC를 실제 실행했는가? | □ |
| Fail 건을 Bug Report로 등록했는가? | □ |
| 수정 버그를 Retest했는가? | □ |
| Critical/Major Bug가 Gate를 통과하는가? | □ |
| curl/Postman으로 API 3종을 검증했는가? | □ |
| DB에서 threshold_result.is_red_zone을 확인했는가? | □ |
| Results 화면 Red Zone 배지를 눈으로 확인했는가? | □ |
| 배포 전 P0 Regression을 수행했는가? | □ |

---

## 20. 자동화 권장 (다음 단계)

| 우선순위 | 대상 | 도구 |
| --- | --- | --- |
| P0 | `calculate_rir`, `classify_housing_status` | pytest |
| P0 | `SimulationSessionService`, `SimulationEngineService` | JUnit + @SpringBootTest |
| P1 | POST sessions, run, GET results | REST Assured |
| P1 | Home→Results | Playwright |

---

**MVP QA 한 줄:** *TC-003(RIR 0.45 → Red Zone)과 TC-011(E2E)이 Pass면 MVP 릴리즈 후보.*
