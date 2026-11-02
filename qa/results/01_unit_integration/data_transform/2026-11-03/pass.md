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
