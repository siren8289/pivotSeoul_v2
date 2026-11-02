# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261103-015624-f1a2 QA-E2E-FLOW-001

- TC_ID: QA-E2E-FLOW-001
- 실행시각: 2026-11-03T01:56:24+09:00
- area: 02_web_api
- section: diagnosis_input
- 기능명: user_journey_e2e
- 도구A: node-e2e / PASS / node --test front/tests/e2e_flow.test.mjs
- 도구B: e2e-flow-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/e2e_flow_check.py
- 범위: 진단 생성→조회→추천→오류 응답 전체 사용자 여정을 교차 검증한다.
- GitCommit: 33fa0b0+dirty
- 파일: front/src/pages/DiagnosePage.tsx
- 함수: handleSubmit
- 줄번호: 25
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: 진단 생성→조회→추천→오류 응답 전체 사용자 여정을 교차 검증한다.
- 실제결과: 진단 생성→조회→추천→오류 응답 전체 사용자 여정을 교차 검증한다. | A `node --test front/tests/e2e_flow.test.mjs` node --test exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/e2e_flow_check.py` loopback HTTP E2E flow (health, create 201, get 200, 404, 400, recommend 25 districts) held | 두 도구 PASS
