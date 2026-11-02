# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261103-015624-f1a2 QA-INT-PIPELINE-001

- TC_ID: QA-INT-PIPELINE-001
- 실행시각: 2026-11-03T01:56:24+09:00
- area: 01_unit_integration
- section: db_persist
- 기능명: service_integration
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_integration_pipeline.py -q --tb=line
- 도구B: integration-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/integration_check.py
- 범위: Data ↔ AI ↔ Back ↔ Front 통합 정합성을 두 도구로 확인한다.
- GitCommit: 33fa0b0+dirty
- 파일: back/src/main/java/com/pivotseoul/diagnosis/service/DiagnosisService.java
- 함수: diagnose
- 줄번호: 32
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: Data ↔ AI ↔ Back ↔ Front 통합 정합성을 두 도구로 확인한다.
- 실제결과: Data ↔ AI ↔ Back ↔ Front 통합 정합성을 두 도구로 확인한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_integration_pipeline.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/integration_check.py` Data-AI-Back-Front 25 districts, conversion rate, and schema mapping aligned | 두 도구 PASS

## R20261103-025113-52fb QA-INT-PIPELINE-001

- TC_ID: QA-INT-PIPELINE-001
- FEATURE_ID: FEAT-INT-PIPELINE
- REQUIREMENT_ID: REQ-INT-MAP
- 실행시각: 2026-11-03T02:54:29+09:00 ~ 2026-11-03T02:55:05+09:00
- area: 01_unit_integration
- section: db_persist
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_integration_pipeline.py -q --tb=line
- 도구B: integration-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/integration_check.py
- 기대결과: Data↔AI↔Back↔Front 필드·구 매핑이 두 독립 경로에서 일치
- 실제결과: 통합 블랙박스. Testcontainers DB는 Spring 테스트에 위임. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_integration_pipeline.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/integration_check.py` Data-AI-Back-Front 25 districts, conversion rate, and schema mapping aligned | 두 도구 PASS
- 증거: qa/results/01_unit_integration/db_persist/2026-11-03
- GitCommit: a51551f+dirty
- 파일: back/src/main/java/com/pivotseoul/diagnosis/service/DiagnosisService.java
- 함수: diagnose
- 줄번호: 32
- RISK_ID: 
- 검증목적: 서로 다른 두 경로의 필수 단언 통과

## R20261103-035418-0890 QA-INT-PIPELINE-001

- TC_ID: QA-INT-PIPELINE-001
- 최종상태: PASS
- 도구A: PASS
- 도구B: PASS
- 실제결과: 통합 블랙박스. Testcontainers DB는 Spring 테스트에 위임. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_integration_pipeline.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/integration_check.py` Data-AI-Back-Front 25 districts, conversion rate, and schema mapping aligned | 두 도구 PASS
