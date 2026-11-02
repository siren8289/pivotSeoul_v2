# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261102-225309-bc64 QA-INT-PIPELINE-001

- TC_ID: QA-INT-PIPELINE-001
- 실행시각: 2026-11-02T22:53:09+09:00
- 기능명: service-integration
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_integration_pipeline.py -q --tb=line
- 도구B: integration-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/integration_check.py
- 범위: Data(전환율·25개 구) ↔ AI(RIR·모델 피처) ↔ Back(snake_case↔camelCase) ↔ Front(TypeScript 타입) 통합 정합성을 두 도구로 확인한다.
- GitCommit: cf3bf07+dirty
- 파일: back/src/main/java/com/pivotseoul/diagnosis/service/DiagnosisService.java
- 함수: diagnose
- 줄번호: 32
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: Data(전환율·25개 구) ↔ AI(RIR·모델 피처) ↔ Back(snake_case↔camelCase) ↔ Front(TypeScript 타입) 통합 정합성을 두 도구로 확인한다.
- 실제결과: Data(전환율·25개 구) ↔ AI(RIR·모델 피처) ↔ Back(snake_case↔camelCase) ↔ Front(TypeScript 타입) 통합 정합성을 두 도구로 확인한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_integration_pipeline.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/integration_check.py` Data-AI-Back-Front 25 districts, conversion rate, and schema mapping aligned | 두 도구 PASS

## R20261102-225401-7abf QA-INT-PIPELINE-001

- TC_ID: QA-INT-PIPELINE-001
- 실행시각: 2026-11-02T22:54:01+09:00
- 기능명: service-integration
- 도구A: pytest / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_integration_pipeline.py -q --tb=line
- 도구B: integration-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/integration_check.py
- 범위: Data(전환율·25개 구) ↔ AI(RIR·모델 피처) ↔ Back(snake_case↔camelCase) ↔ Front(TypeScript 타입) 통합 정합성을 두 도구로 확인한다.
- GitCommit: c927518+dirty
- 파일: back/src/main/java/com/pivotseoul/diagnosis/service/DiagnosisService.java
- 함수: diagnose
- 줄번호: 32
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: Data(전환율·25개 구) ↔ AI(RIR·모델 피처) ↔ Back(snake_case↔camelCase) ↔ Front(TypeScript 타입) 통합 정합성을 두 도구로 확인한다.
- 실제결과: Data(전환율·25개 구) ↔ AI(RIR·모델 피처) ↔ Back(snake_case↔camelCase) ↔ Front(TypeScript 타입) 통합 정합성을 두 도구로 확인한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python -m pytest qa/tests/test_integration_pipeline.py -q --tb=line` pytest exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/integration_check.py` Data-AI-Back-Front 25 districts, conversion rate, and schema mapping aligned | 두 도구 PASS
