# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261102-201549-c42d QA-UNIT-DATA-001

- TC_ID: QA-UNIT-DATA-001
- 실행시각: 2026-11-02T20:15:49+09:00
- 기능명: data-etl
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line
- 도구B: invariant-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py
- 범위: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- GitCommit: 617dca2
- 파일: data/etl/transform.py
- 함수: calc_monthly_cost
- 줄번호: 23
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- 실제결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py` 9 invariants held | 두 도구 PASS

## R20261102-201549-c42d QA-UNIT-RECORD-001

- TC_ID: QA-UNIT-RECORD-001
- 실행시각: 2026-11-02T20:15:49+09:00
- 기능명: qa-recorder
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests -q --tb=line
- 도구B: record-selfcheck / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py
- 범위: pytest는 qa/tests. record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- GitCommit: 617dca2
- 파일: qa/record.py
- 함수: append_results
- 줄번호: 45
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 qa/tests. record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- 실제결과: pytest는 qa/tests. record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py` append, BOM, PASS rule, and HIGH gate held | 두 도구 PASS

## R20261102-222809-8f28 QA-UNIT-DATA-001

- TC_ID: QA-UNIT-DATA-001
- 실행시각: 2026-11-02T22:28:09+09:00
- 기능명: data-etl
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line
- 도구B: invariant-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py
- 범위: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- GitCommit: b2be50a
- 파일: data/etl/transform.py
- 함수: calc_monthly_cost
- 줄번호: 23
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.
- 실제결과: pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest data/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/invariant_check.py` 9 invariants held | 두 도구 PASS

## R20261102-222809-8f28 QA-UNIT-RECORD-001

- TC_ID: QA-UNIT-RECORD-001
- 실행시각: 2026-11-02T22:28:09+09:00
- 기능명: qa-recorder
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests -q --tb=line
- 도구B: record-selfcheck / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py
- 범위: pytest는 qa/tests. record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- GitCommit: b2be50a
- 파일: qa/record.py
- 함수: append_results
- 줄번호: 45
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: pytest는 qa/tests. record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.
- 실제결과: pytest는 qa/tests. record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/record_selfcheck.py` append, BOM, PASS rule, and HIGH gate held | 두 도구 PASS

## R20261102-225309-bc64 QA-UNIT-DATA-001

- TC_ID: QA-UNIT-DATA-001
- 실행시각: 2026-11-02T22:53:09+09:00
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

## R20261102-225309-bc64 QA-UNIT-RECORD-001

- TC_ID: QA-UNIT-RECORD-001
- 실행시각: 2026-11-02T22:53:09+09:00
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

## R20261102-225309-bc64 QA-UNIT-FRONT-001

- TC_ID: QA-UNIT-FRONT-001
- 실행시각: 2026-11-02T22:53:09+09:00
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

## R20261102-225401-7abf QA-UNIT-DATA-001

- TC_ID: QA-UNIT-DATA-001
- 실행시각: 2026-11-02T22:54:01+09:00
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

## R20261102-225401-7abf QA-UNIT-RECORD-001

- TC_ID: QA-UNIT-RECORD-001
- 실행시각: 2026-11-02T22:54:01+09:00
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

## R20261102-225401-7abf QA-UNIT-FRONT-001

- TC_ID: QA-UNIT-FRONT-001
- 실행시각: 2026-11-02T22:54:01+09:00
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
