# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261103-015624-f1a2 QA-API-CONTRACT-001

- TC_ID: QA-API-CONTRACT-001
- 실행시각: 2026-11-03T01:56:24+09:00
- area: 02_web_api
- section: diagnosis_api
- 기능명: api_contract
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_api_contract.py -q --tb=line
- 도구B: api-contract-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/api_contract_check.py
- 범위: AI RIR/통계/설명 규칙 및 Spring Controller·DTO·GlobalExceptionHandler 계약을 교차 검증한다.
- GitCommit: 33fa0b0+dirty
- 파일: ai/src/domain/rir.py
- 함수: classify
- 줄번호: 26
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: AI RIR/통계/설명 규칙 및 Spring Controller·DTO·GlobalExceptionHandler 계약을 교차 검증한다.
- 실제결과: AI RIR/통계/설명 규칙 및 Spring Controller·DTO·GlobalExceptionHandler 계약을 교차 검증한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_api_contract.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/api_contract_check.py` AI RIR/stats/explain & Spring REST API contracts verified | 두 도구 PASS

## R20261103-025113-52fb QA-API-CONTRACT-001

- TC_ID: QA-API-CONTRACT-001
- FEATURE_ID: FEAT-API-CONTRACT
- REQUIREMENT_ID: REQ-API-RIR
- 실행시각: 2026-11-03T02:55:05+09:00 ~ 2026-11-03T02:55:39+09:00
- area: 02_web_api
- section: diagnosis_api
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_api_contract.py -q --tb=line
- 도구B: openapi-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/openapi_check.py
- 기대결과: RIR/계약 pytest와 FastAPI OpenAPI·Controller 표면 검증이 모두 통과
- 실제결과: Schemathesis급 독립 경로로 OpenAPI 스키마 검증 사용 | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_api_contract.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/openapi_check.py` static_routes=8 controllers=3 findings=0 | 두 도구 PASS
- 증거: qa/results/02_web_api/diagnosis_api/2026-11-03
- GitCommit: a51551f+dirty
- 파일: ai/src/api/main.py
- 함수: app
- 줄번호: 20
- RISK_ID: 
- 검증목적: 서로 다른 두 경로의 필수 단언 통과

## R20261103-035924-45a7 QA-API-CONTRACT-001

- TC_ID: QA-API-CONTRACT-001
- 최종상태: PASS
- 도구A: PASS
- 도구B: PASS
- 실제결과: Schemathesis급 독립 경로로 OpenAPI 스키마 검증 사용 | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_api_contract.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/openapi_check.py` static_routes=8 controllers=3 findings=0 | 두 도구 PASS
