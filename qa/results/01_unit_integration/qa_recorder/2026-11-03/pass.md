# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261103-015624-f1a2 QA-UNIT-RECORD-001

- TC_ID: QA-UNIT-RECORD-001
- 실행시각: 2026-11-03T01:56:24+09:00
- area: 01_unit_integration
- section: qa_recorder
- 기능명: qa_recorder
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_record.py qa/tests/test_gate.py qa/tests/test_stop.py -q --tb=line
- 도구B: record-selfcheck / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py
- 범위: pytest는 qa/tests(기록·게이트·Stop hook). record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- GitCommit: 33fa0b0+dirty
- 파일: qa/record.py
- 함수: append_summary
- 줄번호: 49
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 qa/tests(기록·게이트·Stop hook). record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- 실제결과: pytest는 qa/tests(기록·게이트·Stop hook). record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_record.py qa/tests/test_gate.py qa/tests/test_stop.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py` append, BOM, PASS rule, and HIGH gate held | 두 도구 PASS

## R20261103-025113-52fb QA-UNIT-RECORD-001

- TC_ID: QA-UNIT-RECORD-001
- FEATURE_ID: FEAT-QA-RECORD
- REQUIREMENT_ID: REQ-QA-V3
- 실행시각: 2026-11-03T02:53:51+09:00 ~ 2026-11-03T02:54:02+09:00
- area: 01_unit_integration
- section: qa_recorder
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_record.py qa/tests/test_gate.py qa/tests/test_stop.py -q --tb=line
- 도구B: record-selfcheck / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py
- 기대결과: results.tsv 누적·BOM·PASS 규칙·HIGH 게이트가 두 경로에서 통과
- 실제결과: 기록기 단위·게이트 교차 검증 | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_record.py qa/tests/test_gate.py qa/tests/test_stop.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py` append, BOM, PASS rule, and HIGH gate held | 두 도구 PASS
- 증거: qa/results/01_unit_integration/qa_recorder/2026-11-03
- GitCommit: a51551f+dirty
- 파일: qa/record.py
- 함수: append_results
- 줄번호: 125
- RISK_ID: 
- 검증목적: 서로 다른 두 경로의 필수 단언 통과

## R20261103-035418-0890 QA-UNIT-RECORD-001

- TC_ID: QA-UNIT-RECORD-001
- 최종상태: PASS
- 도구A: PASS
- 도구B: PASS
- 실제결과: 기록기 단위·게이트 교차 검증 | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_record.py qa/tests/test_gate.py qa/tests/test_stop.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py` append, BOM, PASS rule, and HIGH gate held | 두 도구 PASS

## R20261103-040635-325a QA-UNIT-RECORD-001

- TC_ID: QA-UNIT-RECORD-001
- FEATURE_ID: FEAT-QA-RECORD
- REQUIREMENT_ID: REQ-QA-V3
- 실행시각: 2026-11-03T04:07:31+09:00 ~ 2026-11-03T04:07:44+09:00
- area: 01_unit_integration
- section: qa_recorder
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_record.py qa/tests/test_gate.py qa/tests/test_stop.py -q --tb=line
- 도구B: record-selfcheck / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py
- 기대결과: results.tsv 누적·BOM·PASS 규칙·HIGH 게이트가 두 경로에서 통과
- 실제결과: 기록기 단위·게이트 교차 검증 | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_record.py qa/tests/test_gate.py qa/tests/test_stop.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py` append, BOM, PASS rule, and HIGH gate held | 두 도구 PASS
- 증거: qa/results/01_unit_integration/qa_recorder/2026-11-03
- GitCommit: d494050
- 파일: qa/record.py
- 함수: append_results
- 줄번호: 125
- RISK_ID: 
- 검증목적: 서로 다른 두 경로의 필수 단언 통과
