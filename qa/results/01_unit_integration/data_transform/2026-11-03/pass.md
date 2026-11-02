# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261103-015624-f1a2 QA-UNIT-DATA-001

- TC_ID: QA-UNIT-DATA-001
- 실행시각: 2026-11-03T01:56:24+09:00
- area: 01_unit_integration
- section: data_transform
- 기능명: data_etl
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line
- 도구B: invariant-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py
- 범위: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- GitCommit: 33fa0b0+dirty
- 파일: data/etl/transform.py
- 함수: calc_monthly_cost
- 줄번호: 23
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- 실제결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py` 9 invariants held | 두 도구 PASS

## R20261103-025113-52fb QA-UNIT-DATA-001

- TC_ID: QA-UNIT-DATA-001
- FEATURE_ID: FEAT-DATA-ETL
- REQUIREMENT_ID: REQ-DATA-TRANSFORM
- 실행시각: 2026-11-03T02:51:25+09:00 ~ 2026-11-03T02:53:51+09:00
- area: 01_unit_integration
- section: data_transform
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line
- 도구B: invariant-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py
- 기대결과: 월 환산 주거비·빈 주소·리스트 변환이 pytest와 invariant-check에서 동일하게 통과
- 실제결과: 1차 pytest(단위) / 2차 invariant 블랙박스. Testcontainers 비적용(순수 변환 로직). | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py` 9 invariants held | 두 도구 PASS
- 증거: qa/results/01_unit_integration/data_transform/2026-11-03
- GitCommit: a51551f+dirty
- 파일: data/etl/transform.py
- 함수: calc_monthly_cost
- 줄번호: 23
- RISK_ID: 
- 검증목적: 서로 다른 두 경로의 필수 단언 통과

## R20261103-035418-0890 QA-UNIT-DATA-001

- TC_ID: QA-UNIT-DATA-001
- 최종상태: PASS
- 도구A: PASS
- 도구B: PASS
- 실제결과: 1차 pytest(단위) / 2차 invariant 블랙박스. Testcontainers 비적용(순수 변환 로직). | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py` 9 invariants held | 두 도구 PASS

## R20261103-040635-325a QA-UNIT-DATA-001

- TC_ID: QA-UNIT-DATA-001
- FEATURE_ID: FEAT-DATA-ETL
- REQUIREMENT_ID: REQ-DATA-TRANSFORM
- 실행시각: 2026-11-03T04:06:36+09:00 ~ 2026-11-03T04:07:31+09:00
- area: 01_unit_integration
- section: data_transform
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line
- 도구B: invariant-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py
- 기대결과: 월 환산 주거비·빈 주소·리스트 변환이 pytest와 invariant-check에서 동일하게 통과
- 실제결과: 1차 pytest(단위) / 2차 invariant 블랙박스. Testcontainers 비적용(순수 변환 로직). | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py` 9 invariants held | 두 도구 PASS
- 증거: qa/results/01_unit_integration/data_transform/2026-11-03
- GitCommit: d494050
- 파일: data/etl/transform.py
- 함수: calc_monthly_cost
- 줄번호: 23
- RISK_ID: 
- 검증목적: 서로 다른 두 경로의 필수 단언 통과
