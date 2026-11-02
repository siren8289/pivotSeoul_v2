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

## R20261103-025113-52fb QA-SEC-SECRET-001

- TC_ID: QA-SEC-SECRET-001
- FEATURE_ID: FEAT-SEC-SECRET
- REQUIREMENT_ID: REQ-SEC-SECRET
- 실행시각: 2026-11-03T02:55:56+09:00 ~ 2026-11-03T02:56:37+09:00
- area: 03_security_quality
- section: nonfunctional_qa
- 도구A: secret-scan / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py
- 도구B: secret-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py
- 기대결과: 고신뢰 비밀값 패턴이 두 독립 스캐너에서 모두 없음
- 실제결과: 비밀정보 전용 이중 패턴. CodeQL/Semgrep과 계층이 다름. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py` secret findings: 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py` git grep secret findings: 0 | 고신뢰 비밀값 패턴 없음
- 증거: qa/results/03_security_quality/nonfunctional_qa/2026-11-03
- GitCommit: a51551f+dirty
- 파일: qa/tools/secret_grep.py
- 함수: scan
- 줄번호: 18
- RISK_ID: 
- 검증목적: 서로 다른 두 경로의 필수 단언 통과

## R20261103-025113-52fb QA-SEC-AUTH-001

- TC_ID: QA-SEC-AUTH-001
- FEATURE_ID: FEAT-SEC-AUTH
- REQUIREMENT_ID: REQ-SEC-AUTH
- 실행시각: 2026-11-03T02:56:37+09:00 ~ 2026-11-03T02:56:41+09:00
- area: 03_security_quality
- section: nonfunctional_qa
- 도구A: auth-surface / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py
- 도구B: auth-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py
- 기대결과: 인증 없는 매핑 목록이 두 도구에서 동일
- 실제결과: 인가 누락 표면. 발견 시 RISK 등록. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py` unauthenticated mappings: 13 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py` git grep unauthenticated mappings: 13 | 인증 없는 매핑 13건을 두 도구가 같이 찾음
- 증거: qa/results/03_security_quality/nonfunctional_qa/2026-11-03
- GitCommit: a51551f+dirty
- 파일: back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java
- 함수: get
- 줄번호: 39
- RISK_ID: RISK-SEC-001
- 검증목적: 서로 다른 두 경로의 필수 단언 통과

## R20261103-025113-52fb QA-SEC-SEMGREP-001

- TC_ID: QA-SEC-SEMGREP-001
- FEATURE_ID: FEAT-SEC-SAST
- REQUIREMENT_ID: REQ-SEC-SAST
- 실행시각: 2026-11-03T02:56:42+09:00 ~ 2026-11-03T02:57:42+09:00
- area: 03_security_quality
- section: nonfunctional_qa
- 도구A: semgrep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/semgrep_check.py
- 도구B: secret-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py
- 기대결과: Semgrep SAST와 비밀값 grep이 각각 실행되고 치명 소견 없음
- 실제결과: CodeQL은 GitHub Actions codeql job으로 2차 공식 경로. 로컬은 Semgrep+secret-grep. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/semgrep_check.py` semgrep findings=0 exit=0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py` git grep secret findings: 0 | 두 도구 PASS
- 증거: qa/results/03_security_quality/nonfunctional_qa/2026-11-03
- GitCommit: a51551f+dirty
- 파일: qa/tools/secret_grep.py
- 함수: scan
- 줄번호: 18
- RISK_ID: RISK-V3-CODEQL
- 검증목적: 서로 다른 두 경로의 필수 단언 통과

## R20261103-025113-52fb QA-PERF-BENCH-001

- TC_ID: QA-PERF-BENCH-001
- FEATURE_ID: FEAT-PERF
- REQUIREMENT_ID: REQ-PERF-LOCAL
- 실행시각: 2026-11-03T02:57:42+09:00 ~ 2026-11-03T02:57:49+09:00
- area: 03_security_quality
- section: nonfunctional_qa
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_performance.py -q --tb=line
- 도구B: perf-benchmark / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/perf_benchmark.py
- 기대결과: 로컬 마이크로벤치 임계 통과. k6는 스테이징 전용.
- 실제결과: 품질 성능. k6 부하 금지(운영). | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_performance.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/perf_benchmark.py` etl_1000=1.3ms (<500ms), ai_5000=106.4ms (<1000ms) | 두 도구 PASS
- 증거: qa/results/03_security_quality/nonfunctional_qa/2026-11-03
- GitCommit: a51551f+dirty
- 파일: ai/src/domain/district_stats.py
- 함수: find_stat
- 줄번호: 18
- RISK_ID: 
- 검증목적: 서로 다른 두 경로의 필수 단언 통과

## R20261103-040333-4843 QA-SEC-SECRET-001

- TC_ID: QA-SEC-SECRET-001
- 최종상태: PASS
- 도구A: PASS
- 도구B: PASS
- 실제결과: 비밀정보 전용 이중 패턴. CodeQL/Semgrep과 계층이 다름. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py` secret findings: 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py` git grep secret findings: 0 | 고신뢰 비밀값 패턴 없음

## R20261103-040333-4843 QA-SEC-AUTH-001

- TC_ID: QA-SEC-AUTH-001
- 최종상태: PASS
- 도구A: PASS
- 도구B: PASS
- 실제결과: 인가 누락 표면. 발견 시 RISK 등록. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py` unauthenticated mappings: 13 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py` git grep unauthenticated mappings: 13 | 인증 없는 매핑 13건을 두 도구가 같이 찾음

## R20261103-040333-4843 QA-SEC-SEMGREP-001

- TC_ID: QA-SEC-SEMGREP-001
- 최종상태: PASS
- 도구A: PASS
- 도구B: PASS
- 실제결과: CodeQL은 GitHub Actions codeql job으로 2차 공식 경로. 로컬은 Semgrep+secret-grep. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/semgrep_check.py` semgrep findings=0 exit=0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py` git grep secret findings: 0 | 두 도구 PASS

## R20261103-040333-4843 QA-PERF-BENCH-001

- TC_ID: QA-PERF-BENCH-001
- 최종상태: PASS
- 도구A: PASS
- 도구B: PASS
- 실제결과: 품질 성능. k6 부하 금지(운영). | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_performance.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/perf_benchmark.py` etl_1000=6.6ms (<500ms), ai_5000=144.6ms (<1000ms) | 두 도구 PASS

## R20261103-040635-325a QA-SEC-SECRET-001

- TC_ID: QA-SEC-SECRET-001
- FEATURE_ID: FEAT-SEC-SECRET
- REQUIREMENT_ID: REQ-SEC-SECRET
- 실행시각: 2026-11-03T04:09:14+09:00 ~ 2026-11-03T04:09:20+09:00
- area: 03_security_quality
- section: nonfunctional_qa
- 도구A: secret-scan / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py
- 도구B: secret-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py
- 기대결과: 고신뢰 비밀값 패턴이 두 독립 스캐너에서 모두 없음
- 실제결과: 비밀정보 전용 이중 패턴. CodeQL/Semgrep과 계층이 다름. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_scan.py` secret findings: 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py` git grep secret findings: 0 | 고신뢰 비밀값 패턴 없음
- 증거: qa/results/03_security_quality/nonfunctional_qa/2026-11-03
- GitCommit: d494050
- 파일: qa/tools/secret_grep.py
- 함수: scan
- 줄번호: 18
- RISK_ID: 
- 검증목적: 서로 다른 두 경로의 필수 단언 통과

## R20261103-040635-325a QA-SEC-AUTH-001

- TC_ID: QA-SEC-AUTH-001
- FEATURE_ID: FEAT-SEC-AUTH
- REQUIREMENT_ID: REQ-SEC-AUTH
- 실행시각: 2026-11-03T04:09:20+09:00 ~ 2026-11-03T04:09:23+09:00
- area: 03_security_quality
- section: nonfunctional_qa
- 도구A: auth-surface / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py
- 도구B: auth-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py
- 기대결과: 인증 없는 매핑 목록이 두 도구에서 동일
- 실제결과: 인가 누락 표면. 발견 시 RISK 등록. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_surface.py` unauthenticated mappings: 13 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/auth_grep.py` git grep unauthenticated mappings: 13 | 인증 없는 매핑 13건을 두 도구가 같이 찾음
- 증거: qa/results/03_security_quality/nonfunctional_qa/2026-11-03
- GitCommit: d494050
- 파일: back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java
- 함수: get
- 줄번호: 39
- RISK_ID: RISK-SEC-001
- 검증목적: 서로 다른 두 경로의 필수 단언 통과

## R20261103-040635-325a QA-SEC-SEMGREP-001

- TC_ID: QA-SEC-SEMGREP-001
- FEATURE_ID: FEAT-SEC-SAST
- REQUIREMENT_ID: REQ-SEC-SAST
- 실행시각: 2026-11-03T04:09:23+09:00 ~ 2026-11-03T04:10:33+09:00
- area: 03_security_quality
- section: nonfunctional_qa
- 도구A: semgrep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/semgrep_check.py
- 도구B: secret-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py
- 기대결과: Semgrep SAST와 비밀값 grep이 각각 실행되고 치명 소견 없음
- 실제결과: CodeQL은 GitHub Actions codeql job으로 2차 공식 경로. 로컬은 Semgrep+secret-grep. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/semgrep_check.py` semgrep findings=0 exit=0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/secret_grep.py` git grep secret findings: 0 | 두 도구 PASS
- 증거: qa/results/03_security_quality/nonfunctional_qa/2026-11-03
- GitCommit: d494050
- 파일: qa/tools/secret_grep.py
- 함수: scan
- 줄번호: 18
- RISK_ID: RISK-V3-CODEQL
- 검증목적: 서로 다른 두 경로의 필수 단언 통과

## R20261103-040635-325a QA-PERF-BENCH-001

- TC_ID: QA-PERF-BENCH-001
- FEATURE_ID: FEAT-PERF
- REQUIREMENT_ID: REQ-PERF-LOCAL
- 실행시각: 2026-11-03T04:10:33+09:00 ~ 2026-11-03T04:11:19+09:00
- area: 03_security_quality
- section: nonfunctional_qa
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_performance.py -q --tb=line
- 도구B: perf-benchmark / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/perf_benchmark.py
- 기대결과: 로컬 마이크로벤치 임계 통과. k6는 스테이징 전용.
- 실제결과: 품질 성능. k6 부하 금지(운영). | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_performance.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/perf_benchmark.py` etl_1000=0.5ms (<500ms), ai_5000=26.0ms (<1000ms) | 두 도구 PASS
- 증거: qa/results/03_security_quality/nonfunctional_qa/2026-11-03
- GitCommit: d494050
- 파일: ai/src/domain/district_stats.py
- 함수: find_stat
- 줄번호: 18
- RISK_ID: 
- 검증목적: 서로 다른 두 경로의 필수 단언 통과
