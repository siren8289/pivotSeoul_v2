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

## R20261103-025113-52fb QA-UNIT-FRONT-001

- TC_ID: QA-UNIT-FRONT-001
- FEATURE_ID: FEAT-UI-COMMON
- REQUIREMENT_ID: REQ-UI-OPTIONS
- 실행시각: 2026-11-03T02:54:02+09:00 ~ 2026-11-03T02:54:29+09:00
- area: 02_web_api
- section: common_ui
- 도구A: node-test / PASS / node --test front/tests/front_unit.test.mjs
- 도구B: front-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/front_check.py
- 기대결과: 25개 구·옵션·라우트 가드가 node 실행과 정적 검사에서 일치
- 실제결과: Playwright 전환 전 임시 UI 이중 경로. RISK-V3-PLAYWRIGHT 참고. | A `node --test front/tests/front_unit.test.mjs` node --test exit 0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/front_check.py` front options(25 districts), routes, API endpoints, and guards verified | 두 도구 PASS
- 증거: qa/results/02_web_api/common_ui/2026-11-03
- GitCommit: a51551f+dirty
- 파일: front/src/components/options.ts
- 함수: DISTRICTS
- 줄번호: 16
- RISK_ID: RISK-V3-PLAYWRIGHT
- 검증목적: 서로 다른 두 경로의 필수 단언 통과
