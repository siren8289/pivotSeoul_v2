# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261103-015624-f1a2 QA-SEC-SECRET-001

- TC_ID: QA-SEC-SECRET-001
- 실행시각: 2026-11-03T01:56:24+09:00
- area: 03_security_quality
- section: nonfunctional_qa
- 기능명: secrets
- 도구A: secret-scan / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py
- 도구B: secret-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py
- 범위: 추적 중인 텍스트 파일의 고신뢰 비밀값 패턴. 두 도구가 패턴을 각자 가진다.
- GitCommit: 33fa0b0+dirty
- 파일: qa/tools/secret_grep.py
- 함수: scan
- 줄번호: 18
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: 추적 중인 텍스트 파일의 고신뢰 비밀값 패턴. 두 도구가 패턴을 각자 가진다.
- 실제결과: 추적 중인 텍스트 파일의 고신뢰 비밀값 패턴. 두 도구가 패턴을 각자 가진다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py` secret findings: 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py` git grep secret findings: 0 | 고신뢰 비밀값 패턴 없음

## R20261103-015624-f1a2 QA-SEC-AUTH-001

- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-03T01:56:24+09:00
- area: 03_security_quality
- section: nonfunctional_qa
- 기능명: api_auth
- 도구A: auth-surface / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py
- 도구B: auth-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py
- 범위: back/src/main 과 ai/src 의 매핑. /health 는 제외. 인증 정책이 없어 발견은 RISK다.
- GitCommit: 33fa0b0+dirty
- 파일: back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java
- 함수: get
- 줄번호: 39
- ISSUE_ID: 
- RISK_ID: RISK-SEC-001
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: back/src/main 과 ai/src 의 매핑. /health 는 제외. 인증 정책이 없어 발견은 RISK다.
- 실제결과: back/src/main 과 ai/src 의 매핑. /health 는 제외. 인증 정책이 없어 발견은 RISK다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py` unauthenticated mappings: 13 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py` git grep unauthenticated mappings: 13 | 인증 없는 매핑 13건을 두 도구가 같이 찾음

## R20261103-015624-f1a2 QA-PERF-BENCH-001

- TC_ID: QA-PERF-BENCH-001
- 실행시각: 2026-11-03T01:56:24+09:00
- area: 03_security_quality
- section: nonfunctional_qa
- 기능명: performance_benchmark
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_performance.py -q --tb=line
- 도구B: perf-benchmark / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/perf_benchmark.py
- 범위: ETL·AI 통계/RIR 성능을 두 도구로 측정한다.
- GitCommit: 33fa0b0+dirty
- 파일: ai/src/domain/district_stats.py
- 함수: find_stat
- 줄번호: 18
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: ETL·AI 통계/RIR 성능을 두 도구로 측정한다.
- 실제결과: ETL·AI 통계/RIR 성능을 두 도구로 측정한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_performance.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/perf_benchmark.py` etl_1000=0.8ms (<500ms), ai_5000=33.6ms (<1000ms) | 두 도구 PASS
