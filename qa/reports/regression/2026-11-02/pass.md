# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261102-201603-7ca2 QA-UNIT-DATA-001

- TC_ID: QA-UNIT-DATA-001
- 실행시각: 2026-11-02T20:16:03+09:00
- 기능명: data-etl
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line
- 도구B: invariant-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py
- 범위: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- GitCommit: 7d503cd
- 파일: data/etl/transform.py
- 함수: calc_monthly_cost
- 줄번호: 23
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- 실제결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py` 9 invariants held | 두 도구 PASS

## R20261102-201603-7ca2 QA-UNIT-RECORD-001

- TC_ID: QA-UNIT-RECORD-001
- 실행시각: 2026-11-02T20:16:03+09:00
- 기능명: qa-recorder
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests -q --tb=line
- 도구B: record-selfcheck / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py
- 범위: pytest는 qa/tests. record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- GitCommit: 7d503cd
- 파일: qa/record.py
- 함수: append_results
- 줄번호: 45
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 qa/tests. record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- 실제결과: pytest는 qa/tests. record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py` append, BOM, PASS rule, and HIGH gate held | 두 도구 PASS

## R20261102-201603-7ca2 QA-SEC-SECRET-001

- TC_ID: QA-SEC-SECRET-001
- 실행시각: 2026-11-02T20:16:03+09:00
- 기능명: secrets
- 도구A: secret-scan / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py
- 도구B: secret-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py
- 범위: 추적 중인 텍스트 파일의 개인키, AKIA, AIza, ghp_ 패턴. 두 도구가 패턴을 각자 가진다.
- GitCommit: 7d503cd
- 파일: qa/tools/secret_grep.py
- 함수: scan
- 줄번호: 18
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: 추적 중인 텍스트 파일의 개인키, AKIA, AIza, ghp_ 패턴. 두 도구가 패턴을 각자 가진다.
- 실제결과: 추적 중인 텍스트 파일의 개인키, AKIA, AIza, ghp_ 패턴. 두 도구가 패턴을 각자 가진다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py` secret findings: 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py` git grep secret findings: 0 | 고신뢰 비밀값 패턴 없음

## R20261102-201603-7ca2 QA-SEC-AUTH-001

- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-02T20:16:03+09:00
- 기능명: api-auth
- 도구A: auth-surface / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py
- 도구B: auth-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py
- 범위: back/src/main 과 ai/src 의 매핑. /health 는 상태 확인이라 제외한다. 인증 정책이 없어 발견은 RISK다.
- GitCommit: 7d503cd
- 파일: back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java
- 함수: get
- 줄번호: 39
- ISSUE_ID: 
- RISK_ID: RISK-SEC-001
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: back/src/main 과 ai/src 의 매핑. /health 는 상태 확인이라 제외한다. 인증 정책이 없어 발견은 RISK다.
- 실제결과: back/src/main 과 ai/src 의 매핑. /health 는 상태 확인이라 제외한다. 인증 정책이 없어 발견은 RISK다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py` unauthenticated mappings: 13 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py` git grep unauthenticated mappings: 13 | 인증 없는 매핑 13건을 두 도구가 같이 찾음

## R20261102-222811-3229 QA-UNIT-DATA-001

- TC_ID: QA-UNIT-DATA-001
- 실행시각: 2026-11-02T22:28:11+09:00
- 기능명: data-etl
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line
- 도구B: invariant-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py
- 범위: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- GitCommit: b2be50a+dirty
- 파일: data/etl/transform.py
- 함수: calc_monthly_cost
- 줄번호: 23
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- 실제결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py` 9 invariants held | 두 도구 PASS

## R20261102-222811-3229 QA-UNIT-RECORD-001

- TC_ID: QA-UNIT-RECORD-001
- 실행시각: 2026-11-02T22:28:11+09:00
- 기능명: qa-recorder
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests -q --tb=line
- 도구B: record-selfcheck / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py
- 범위: pytest는 qa/tests. record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- GitCommit: b2be50a+dirty
- 파일: qa/record.py
- 함수: append_results
- 줄번호: 45
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 qa/tests. record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- 실제결과: pytest는 qa/tests. record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py` append, BOM, PASS rule, and HIGH gate held | 두 도구 PASS

## R20261102-222811-3229 QA-SEC-SECRET-001

- TC_ID: QA-SEC-SECRET-001
- 실행시각: 2026-11-02T22:28:11+09:00
- 기능명: secrets
- 도구A: secret-scan / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py
- 도구B: secret-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py
- 범위: 추적 중인 텍스트 파일의 개인키, AKIA, AIza, ghp_ 패턴. 두 도구가 패턴을 각자 가진다.
- GitCommit: b2be50a+dirty
- 파일: qa/tools/secret_grep.py
- 함수: scan
- 줄번호: 18
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: 추적 중인 텍스트 파일의 개인키, AKIA, AIza, ghp_ 패턴. 두 도구가 패턴을 각자 가진다.
- 실제결과: 추적 중인 텍스트 파일의 개인키, AKIA, AIza, ghp_ 패턴. 두 도구가 패턴을 각자 가진다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py` secret findings: 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py` git grep secret findings: 0 | 고신뢰 비밀값 패턴 없음

## R20261102-222811-3229 QA-SEC-AUTH-001

- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-02T22:28:11+09:00
- 기능명: api-auth
- 도구A: auth-surface / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py
- 도구B: auth-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py
- 범위: back/src/main 과 ai/src 의 매핑. /health 는 상태 확인이라 제외한다. 인증 정책이 없어 발견은 RISK다.
- GitCommit: b2be50a+dirty
- 파일: back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java
- 함수: get
- 줄번호: 39
- ISSUE_ID: 
- RISK_ID: RISK-SEC-001
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: back/src/main 과 ai/src 의 매핑. /health 는 상태 확인이라 제외한다. 인증 정책이 없어 발견은 RISK다.
- 실제결과: back/src/main 과 ai/src 의 매핑. /health 는 상태 확인이라 제외한다. 인증 정책이 없어 발견은 RISK다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py` unauthenticated mappings: 13 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py` git grep unauthenticated mappings: 13 | 인증 없는 매핑 13건을 두 도구가 같이 찾음

## R20261102-225315-2e02 QA-UNIT-DATA-001

- TC_ID: QA-UNIT-DATA-001
- 실행시각: 2026-11-02T22:53:15+09:00
- 기능명: data-etl
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line
- 도구B: invariant-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py
- 범위: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- GitCommit: cf3bf07+dirty
- 파일: data/etl/transform.py
- 함수: calc_monthly_cost
- 줄번호: 23
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- 실제결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py` 9 invariants held | 두 도구 PASS

## R20261102-225315-2e02 QA-UNIT-RECORD-001

- TC_ID: QA-UNIT-RECORD-001
- 실행시각: 2026-11-02T22:53:15+09:00
- 기능명: qa-recorder
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_record.py qa/tests/test_gate.py qa/tests/test_stop.py -q --tb=line
- 도구B: record-selfcheck / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py
- 범위: pytest는 qa/tests(기록·게이트·Stop hook). record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- GitCommit: cf3bf07+dirty
- 파일: qa/record.py
- 함수: append_results
- 줄번호: 45
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 qa/tests(기록·게이트·Stop hook). record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- 실제결과: pytest는 qa/tests(기록·게이트·Stop hook). record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_record.py qa/tests/test_gate.py qa/tests/test_stop.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py` append, BOM, PASS rule, and HIGH gate held | 두 도구 PASS

## R20261102-225315-2e02 QA-UNIT-FRONT-001

- TC_ID: QA-UNIT-FRONT-001
- 실행시각: 2026-11-02T22:53:15+09:00
- 기능명: front
- 도구A: node-test / PASS / node --test front/tests/front_unit.test.mjs
- 도구B: front-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/front_check.py
- 범위: node --test는 options.ts·api.ts를 실제 실행한다. front-check는 25개 구·라우트·입력 가드를 정적 검증한다.
- GitCommit: cf3bf07+dirty
- 파일: front/src/components/options.ts
- 함수: DISTRICTS
- 줄번호: 16
- ISSUE_ID: 
- RISK_ID: RISK-QA-001
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: node --test는 options.ts·api.ts를 실제 실행한다. front-check는 25개 구·라우트·입력 가드를 정적 검증한다.
- 실제결과: node --test는 options.ts·api.ts를 실제 실행한다. front-check는 25개 구·라우트·입력 가드를 정적 검증한다. | A `node --test front/tests/front_unit.test.mjs` node --test exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/front_check.py` front options(25 districts), routes, API endpoints, and guards verified | 두 도구 PASS

## R20261102-225315-2e02 QA-API-CONTRACT-001

- TC_ID: QA-API-CONTRACT-001
- 실행시각: 2026-11-02T22:53:15+09:00
- 기능명: api-contract
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_api_contract.py -q --tb=line
- 도구B: api-contract-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/api_contract_check.py
- 범위: pytest와 api-contract-check 두 도구로 AI RIR/통계/설명 규칙 및 Spring Controller·DTO·GlobalExceptionHandler 계약을 교차 검증한다.
- GitCommit: cf3bf07+dirty
- 파일: ai/src/domain/rir.py
- 함수: classify
- 줄번호: 26
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest와 api-contract-check 두 도구로 AI RIR/통계/설명 규칙 및 Spring Controller·DTO·GlobalExceptionHandler 계약을 교차 검증한다.
- 실제결과: pytest와 api-contract-check 두 도구로 AI RIR/통계/설명 규칙 및 Spring Controller·DTO·GlobalExceptionHandler 계약을 교차 검증한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_api_contract.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/api_contract_check.py` AI RIR/stats/explain & Spring REST API contracts verified | 두 도구 PASS

## R20261102-225315-2e02 QA-INT-PIPELINE-001

- TC_ID: QA-INT-PIPELINE-001
- 실행시각: 2026-11-02T22:53:15+09:00
- 기능명: service-integration
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_integration_pipeline.py -q --tb=line
- 도구B: integration-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/integration_check.py
- 범위: Data(전환율·25개 구) ↔ AI(RIR·모델 피처) ↔ Back(snake_case↔camelCase) ↔ Front(TypeScript 타입) 통합 정합성을 두 도구로 확인한다.
- GitCommit: cf3bf07+dirty
- 파일: back/src/main/java/com/pivotseoul/diagnosis/service/DiagnosisService.java
- 함수: diagnose
- 줄번호: 32
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: Data(전환율·25개 구) ↔ AI(RIR·모델 피처) ↔ Back(snake_case↔camelCase) ↔ Front(TypeScript 타입) 통합 정합성을 두 도구로 확인한다.
- 실제결과: Data(전환율·25개 구) ↔ AI(RIR·모델 피처) ↔ Back(snake_case↔camelCase) ↔ Front(TypeScript 타입) 통합 정합성을 두 도구로 확인한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_integration_pipeline.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/integration_check.py` Data-AI-Back-Front 25 districts, conversion rate, and schema mapping aligned | 두 도구 PASS

## R20261102-225315-2e02 QA-E2E-FLOW-001

- TC_ID: QA-E2E-FLOW-001
- 실행시각: 2026-11-02T22:53:15+09:00
- 기능명: user-journey-e2e
- 도구A: node-e2e / PASS / node --test front/tests/e2e_flow.test.mjs
- 도구B: e2e-flow-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/e2e_flow_check.py
- 범위: 진단 생성(201)→상세 조회(200)→25개 자치구 추천(200)→검증 오류(400)/미존재(404) 전체 사용자 여정을 Node E2E와 Python 루프백 HTTP 서버로 교차 검증한다.
- GitCommit: cf3bf07+dirty
- 파일: front/src/pages/DiagnosePage.tsx
- 함수: handleSubmit
- 줄번호: 25
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: 진단 생성(201)→상세 조회(200)→25개 자치구 추천(200)→검증 오류(400)/미존재(404) 전체 사용자 여정을 Node E2E와 Python 루프백 HTTP 서버로 교차 검증한다.
- 실제결과: 진단 생성(201)→상세 조회(200)→25개 자치구 추천(200)→검증 오류(400)/미존재(404) 전체 사용자 여정을 Node E2E와 Python 루프백 HTTP 서버로 교차 검증한다. | A `node --test front/tests/e2e_flow.test.mjs` node --test exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/e2e_flow_check.py` loopback HTTP E2E flow (health, create 201, get 200, 404, 400, recommend 25 districts) held | 두 도구 PASS

## R20261102-225315-2e02 QA-SEC-SECRET-001

- TC_ID: QA-SEC-SECRET-001
- 실행시각: 2026-11-02T22:53:15+09:00
- 기능명: secrets
- 도구A: secret-scan / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py
- 도구B: secret-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py
- 범위: 추적 중인 텍스트 파일의 개인키, AKIA, AIza, ghp_ 패턴. 두 도구가 패턴을 각자 가진다.
- GitCommit: cf3bf07+dirty
- 파일: qa/tools/secret_grep.py
- 함수: scan
- 줄번호: 18
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: 추적 중인 텍스트 파일의 개인키, AKIA, AIza, ghp_ 패턴. 두 도구가 패턴을 각자 가진다.
- 실제결과: 추적 중인 텍스트 파일의 개인키, AKIA, AIza, ghp_ 패턴. 두 도구가 패턴을 각자 가진다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py` secret findings: 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py` git grep secret findings: 0 | 고신뢰 비밀값 패턴 없음

## R20261102-225315-2e02 QA-SEC-AUTH-001

- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-02T22:53:15+09:00
- 기능명: api-auth
- 도구A: auth-surface / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py
- 도구B: auth-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py
- 범위: back/src/main 과 ai/src 의 매핑. /health 는 상태 확인이라 제외한다. 인증 정책이 없어 발견은 RISK다.
- GitCommit: cf3bf07+dirty
- 파일: back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java
- 함수: get
- 줄번호: 39
- ISSUE_ID: 
- RISK_ID: RISK-SEC-001
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: back/src/main 과 ai/src 의 매핑. /health 는 상태 확인이라 제외한다. 인증 정책이 없어 발견은 RISK다.
- 실제결과: back/src/main 과 ai/src 의 매핑. /health 는 상태 확인이라 제외한다. 인증 정책이 없어 발견은 RISK다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py` unauthenticated mappings: 13 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py` git grep unauthenticated mappings: 13 | 인증 없는 매핑 13건을 두 도구가 같이 찾음

## R20261102-225315-2e02 QA-PERF-BENCH-001

- TC_ID: QA-PERF-BENCH-001
- 실행시각: 2026-11-02T22:53:15+09:00
- 기능명: performance-benchmark
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_performance.py -q --tb=line
- 도구B: perf-benchmark / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/perf_benchmark.py
- 범위: ETL 월 주거비 변환·자치구 추출(1,000회 <500ms) 및 AI 25개 구 통계·RIR 판정(5,000회 <1,000ms) 성능을 두 도구로 측정한다.
- GitCommit: cf3bf07+dirty
- 파일: ai/src/domain/district_stats.py
- 함수: find_stat
- 줄번호: 18
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: ETL 월 주거비 변환·자치구 추출(1,000회 <500ms) 및 AI 25개 구 통계·RIR 판정(5,000회 <1,000ms) 성능을 두 도구로 측정한다.
- 실제결과: ETL 월 주거비 변환·자치구 추출(1,000회 <500ms) 및 AI 25개 구 통계·RIR 판정(5,000회 <1,000ms) 성능을 두 도구로 측정한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_performance.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/perf_benchmark.py` etl_1000=0.6ms (<500ms), ai_5000=13.6ms (<1000ms) | 두 도구 PASS

## R20261102-225405-4684 QA-UNIT-DATA-001

- TC_ID: QA-UNIT-DATA-001
- 실행시각: 2026-11-02T22:54:05+09:00
- 기능명: data-etl
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line
- 도구B: invariant-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py
- 범위: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- GitCommit: c927518+dirty
- 파일: data/etl/transform.py
- 함수: calc_monthly_cost
- 줄번호: 23
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- 실제결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py` 9 invariants held | 두 도구 PASS

## R20261102-225405-4684 QA-UNIT-RECORD-001

- TC_ID: QA-UNIT-RECORD-001
- 실행시각: 2026-11-02T22:54:05+09:00
- 기능명: qa-recorder
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_record.py qa/tests/test_gate.py qa/tests/test_stop.py -q --tb=line
- 도구B: record-selfcheck / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py
- 범위: pytest는 qa/tests(기록·게이트·Stop hook). record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- GitCommit: c927518+dirty
- 파일: qa/record.py
- 함수: append_results
- 줄번호: 45
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 qa/tests(기록·게이트·Stop hook). record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- 실제결과: pytest는 qa/tests(기록·게이트·Stop hook). record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_record.py qa/tests/test_gate.py qa/tests/test_stop.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py` append, BOM, PASS rule, and HIGH gate held | 두 도구 PASS

## R20261102-225405-4684 QA-UNIT-FRONT-001

- TC_ID: QA-UNIT-FRONT-001
- 실행시각: 2026-11-02T22:54:05+09:00
- 기능명: front
- 도구A: node-test / PASS / node --test front/tests/front_unit.test.mjs
- 도구B: front-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/front_check.py
- 범위: node --test는 options.ts·api.ts를 실제 실행한다. front-check는 25개 구·라우트·입력 가드를 정적 검증한다.
- GitCommit: c927518+dirty
- 파일: front/src/components/options.ts
- 함수: DISTRICTS
- 줄번호: 16
- ISSUE_ID: 
- RISK_ID: RISK-QA-001
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: node --test는 options.ts·api.ts를 실제 실행한다. front-check는 25개 구·라우트·입력 가드를 정적 검증한다.
- 실제결과: node --test는 options.ts·api.ts를 실제 실행한다. front-check는 25개 구·라우트·입력 가드를 정적 검증한다. | A `node --test front/tests/front_unit.test.mjs` node --test exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/front_check.py` front options(25 districts), routes, API endpoints, and guards verified | 두 도구 PASS

## R20261102-225405-4684 QA-API-CONTRACT-001

- TC_ID: QA-API-CONTRACT-001
- 실행시각: 2026-11-02T22:54:05+09:00
- 기능명: api-contract
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_api_contract.py -q --tb=line
- 도구B: api-contract-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/api_contract_check.py
- 범위: pytest와 api-contract-check 두 도구로 AI RIR/통계/설명 규칙 및 Spring Controller·DTO·GlobalExceptionHandler 계약을 교차 검증한다.
- GitCommit: c927518+dirty
- 파일: ai/src/domain/rir.py
- 함수: classify
- 줄번호: 26
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest와 api-contract-check 두 도구로 AI RIR/통계/설명 규칙 및 Spring Controller·DTO·GlobalExceptionHandler 계약을 교차 검증한다.
- 실제결과: pytest와 api-contract-check 두 도구로 AI RIR/통계/설명 규칙 및 Spring Controller·DTO·GlobalExceptionHandler 계약을 교차 검증한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_api_contract.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/api_contract_check.py` AI RIR/stats/explain & Spring REST API contracts verified | 두 도구 PASS

## R20261102-225405-4684 QA-INT-PIPELINE-001

- TC_ID: QA-INT-PIPELINE-001
- 실행시각: 2026-11-02T22:54:05+09:00
- 기능명: service-integration
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_integration_pipeline.py -q --tb=line
- 도구B: integration-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/integration_check.py
- 범위: Data(전환율·25개 구) ↔ AI(RIR·모델 피처) ↔ Back(snake_case↔camelCase) ↔ Front(TypeScript 타입) 통합 정합성을 두 도구로 확인한다.
- GitCommit: c927518+dirty
- 파일: back/src/main/java/com/pivotseoul/diagnosis/service/DiagnosisService.java
- 함수: diagnose
- 줄번호: 32
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: Data(전환율·25개 구) ↔ AI(RIR·모델 피처) ↔ Back(snake_case↔camelCase) ↔ Front(TypeScript 타입) 통합 정합성을 두 도구로 확인한다.
- 실제결과: Data(전환율·25개 구) ↔ AI(RIR·모델 피처) ↔ Back(snake_case↔camelCase) ↔ Front(TypeScript 타입) 통합 정합성을 두 도구로 확인한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_integration_pipeline.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/integration_check.py` Data-AI-Back-Front 25 districts, conversion rate, and schema mapping aligned | 두 도구 PASS

## R20261102-225405-4684 QA-E2E-FLOW-001

- TC_ID: QA-E2E-FLOW-001
- 실행시각: 2026-11-02T22:54:05+09:00
- 기능명: user-journey-e2e
- 도구A: node-e2e / PASS / node --test front/tests/e2e_flow.test.mjs
- 도구B: e2e-flow-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/e2e_flow_check.py
- 범위: 진단 생성(201)→상세 조회(200)→25개 자치구 추천(200)→검증 오류(400)/미존재(404) 전체 사용자 여정을 Node E2E와 Python 루프백 HTTP 서버로 교차 검증한다.
- GitCommit: c927518+dirty
- 파일: front/src/pages/DiagnosePage.tsx
- 함수: handleSubmit
- 줄번호: 25
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: 진단 생성(201)→상세 조회(200)→25개 자치구 추천(200)→검증 오류(400)/미존재(404) 전체 사용자 여정을 Node E2E와 Python 루프백 HTTP 서버로 교차 검증한다.
- 실제결과: 진단 생성(201)→상세 조회(200)→25개 자치구 추천(200)→검증 오류(400)/미존재(404) 전체 사용자 여정을 Node E2E와 Python 루프백 HTTP 서버로 교차 검증한다. | A `node --test front/tests/e2e_flow.test.mjs` node --test exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/e2e_flow_check.py` loopback HTTP E2E flow (health, create 201, get 200, 404, 400, recommend 25 districts) held | 두 도구 PASS

## R20261102-225405-4684 QA-SEC-SECRET-001

- TC_ID: QA-SEC-SECRET-001
- 실행시각: 2026-11-02T22:54:05+09:00
- 기능명: secrets
- 도구A: secret-scan / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py
- 도구B: secret-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py
- 범위: 추적 중인 텍스트 파일의 개인키, AKIA, AIza, ghp_ 패턴. 두 도구가 패턴을 각자 가진다.
- GitCommit: c927518+dirty
- 파일: qa/tools/secret_grep.py
- 함수: scan
- 줄번호: 18
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: 추적 중인 텍스트 파일의 개인키, AKIA, AIza, ghp_ 패턴. 두 도구가 패턴을 각자 가진다.
- 실제결과: 추적 중인 텍스트 파일의 개인키, AKIA, AIza, ghp_ 패턴. 두 도구가 패턴을 각자 가진다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py` secret findings: 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py` git grep secret findings: 0 | 고신뢰 비밀값 패턴 없음

## R20261102-225405-4684 QA-SEC-AUTH-001

- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-02T22:54:05+09:00
- 기능명: api-auth
- 도구A: auth-surface / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py
- 도구B: auth-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py
- 범위: back/src/main 과 ai/src 의 매핑. /health 는 상태 확인이라 제외한다. 인증 정책이 없어 발견은 RISK다.
- GitCommit: c927518+dirty
- 파일: back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java
- 함수: get
- 줄번호: 39
- ISSUE_ID: 
- RISK_ID: RISK-SEC-001
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: back/src/main 과 ai/src 의 매핑. /health 는 상태 확인이라 제외한다. 인증 정책이 없어 발견은 RISK다.
- 실제결과: back/src/main 과 ai/src 의 매핑. /health 는 상태 확인이라 제외한다. 인증 정책이 없어 발견은 RISK다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py` unauthenticated mappings: 13 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py` git grep unauthenticated mappings: 13 | 인증 없는 매핑 13건을 두 도구가 같이 찾음

## R20261102-225405-4684 QA-PERF-BENCH-001

- TC_ID: QA-PERF-BENCH-001
- 실행시각: 2026-11-02T22:54:05+09:00
- 기능명: performance-benchmark
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_performance.py -q --tb=line
- 도구B: perf-benchmark / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/perf_benchmark.py
- 범위: ETL 월 주거비 변환·자치구 추출(1,000회 <500ms) 및 AI 25개 구 통계·RIR 판정(5,000회 <1,000ms) 성능을 두 도구로 측정한다.
- GitCommit: c927518+dirty
- 파일: ai/src/domain/district_stats.py
- 함수: find_stat
- 줄번호: 18
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: ETL 월 주거비 변환·자치구 추출(1,000회 <500ms) 및 AI 25개 구 통계·RIR 판정(5,000회 <1,000ms) 성능을 두 도구로 측정한다.
- 실제결과: ETL 월 주거비 변환·자치구 추출(1,000회 <500ms) 및 AI 25개 구 통계·RIR 판정(5,000회 <1,000ms) 성능을 두 도구로 측정한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_performance.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/perf_benchmark.py` etl_1000=0.4ms (<500ms), ai_5000=9.0ms (<1000ms) | 두 도구 PASS
