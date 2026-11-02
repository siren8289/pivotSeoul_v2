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
