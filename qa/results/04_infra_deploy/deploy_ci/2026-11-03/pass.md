# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261103-015624-f1a2 QA-INFRA-COMPOSE-001

- TC_ID: QA-INFRA-COMPOSE-001
- 실행시각: 2026-11-03T01:56:24+09:00
- area: 04_infra_deploy
- section: deploy_ci
- 기능명: compose
- 도구A: compose-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/compose_check.py
- 도구B: compose-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/compose_grep.py
- 범위: compose.yaml의 db/ai/back/front 구조를 서로 다른 두 정적 도구로 확인한다.
- GitCommit: 33fa0b0+dirty
- 파일: compose.yaml
- 함수: services
- 줄번호: 5
- ISSUE_ID: 
- RISK_ID: 
- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.
- 기대결과: compose.yaml의 db/ai/back/front 구조를 서로 다른 두 정적 도구로 확인한다.
- 실제결과: compose.yaml의 db/ai/back/front 구조를 서로 다른 두 정적 도구로 확인한다. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/compose_check.py` services=['ai', 'back', 'db', 'front'] findings=0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/compose_grep.py` anchors checked=7 findings=0 | 두 도구 PASS

## R20261103-025113-52fb QA-INFRA-COMPOSE-001

- TC_ID: QA-INFRA-COMPOSE-001
- FEATURE_ID: FEAT-INFRA-COMPOSE
- REQUIREMENT_ID: REQ-INFRA-COMPOSE
- 실행시각: 2026-11-03T02:57:49+09:00 ~ 2026-11-03T02:57:50+09:00
- area: 04_infra_deploy
- section: deploy_ci
- 도구A: compose-check / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/compose_check.py
- 도구B: compose-grep / PASS / /Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/compose_grep.py
- 기대결과: db/ai/back/front 서비스·이미지/빌드·의존성 앵커가 두 정적 도구에서 통과
- 실제결과: Compose 설정·구조. 상태/health 라이브는 smoke TC. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/compose_check.py` services=['ai', 'back', 'db', 'front'] findings=0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/compose_grep.py` anchors checked=7 findings=0 | 두 도구 PASS
- 증거: qa/results/04_infra_deploy/deploy_ci/2026-11-03
- GitCommit: a51551f+dirty
- 파일: compose.yaml
- 함수: services
- 줄번호: 5
- RISK_ID: 
- 검증목적: 서로 다른 두 경로의 필수 단언 통과

## R20261103-040456-dcde QA-INFRA-COMPOSE-001

- TC_ID: QA-INFRA-COMPOSE-001
- 최종상태: PASS
- 도구A: PASS
- 도구B: PASS
- 실제결과: Compose 설정·구조. 상태/health 라이브는 smoke TC. | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/compose_check.py` services=['ai', 'back', 'db', 'front'] findings=0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/compose_grep.py` anchors checked=7 findings=0 | 두 도구 PASS
