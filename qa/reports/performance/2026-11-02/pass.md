# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261102-225309-bc64 QA-PERF-BENCH-001

- TC_ID: QA-PERF-BENCH-001
- 실행시각: 2026-11-02T22:53:09+09:00
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
- 실제결과: ETL 월 주거비 변환·자치구 추출(1,000회 <500ms) 및 AI 25개 구 통계·RIR 판정(5,000회 <1,000ms) 성능을 두 도구로 측정한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_performance.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/perf_benchmark.py` etl_1000=0.6ms (<500ms), ai_5000=10.0ms (<1000ms) | 두 도구 PASS

## R20261102-225401-7abf QA-PERF-BENCH-001

- TC_ID: QA-PERF-BENCH-001
- 실행시각: 2026-11-02T22:54:01+09:00
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
- 실제결과: ETL 월 주거비 변환·자치구 추출(1,000회 <500ms) 및 AI 25개 구 통계·RIR 판정(5,000회 <1,000ms) 성능을 두 도구로 측정한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_performance.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/perf_benchmark.py` etl_1000=0.3ms (<500ms), ai_5000=7.7ms (<1000ms) | 두 도구 PASS
