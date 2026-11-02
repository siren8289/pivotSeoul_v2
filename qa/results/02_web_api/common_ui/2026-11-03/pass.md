# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261103-015624-f1a2 QA-UNIT-FRONT-001

- TC_ID: QA-UNIT-FRONT-001
- 실행시각: 2026-11-03T01:56:24+09:00
- area: 02_web_api
- section: common_ui
- 기능명: front
- 도구A: node-test / PASS / node --test front/tests/front_unit.test.mjs
- 도구B: front-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/front_check.py
- 범위: node --test는 options.ts·api.ts를 실제 실행한다. front-check는 25개 구·라우트·입력 가드를 정적 검증한다.
- GitCommit: 33fa0b0+dirty
- 파일: front/src/components/options.ts
- 함수: DISTRICTS
- 줄번호: 16
- ISSUE_ID: 
- RISK_ID: RISK-QA-001
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: node --test는 options.ts·api.ts를 실제 실행한다. front-check는 25개 구·라우트·입력 가드를 정적 검증한다.
- 실제결과: node --test는 options.ts·api.ts를 실제 실행한다. front-check는 25개 구·라우트·입력 가드를 정적 검증한다. | A `node --test front/tests/front_unit.test.mjs` node --test exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/front_check.py` front options(25 districts), routes, API endpoints, and guards verified | 두 도구 PASS
