# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261102-225309-bc64 QA-API-CONTRACT-001

- TC_ID: QA-API-CONTRACT-001
- 실행시각: 2026-11-02T22:53:09+09:00
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

## R20261102-225401-7abf QA-API-CONTRACT-001

- TC_ID: QA-API-CONTRACT-001
- 실행시각: 2026-11-02T22:54:01+09:00
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
