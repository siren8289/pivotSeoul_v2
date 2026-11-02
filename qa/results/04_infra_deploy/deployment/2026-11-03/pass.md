# PASS

통과한 TC. 이전 절은 삭제하지 않는다.

## R20261103-040456-dcde QA-INFRA-SMOKE-001

- TC_ID: QA-INFRA-SMOKE-001
- 최종상태: PASS
- 도구A: PASS
- 도구B: PASS
- 실제결과: 회귀/배포 전. 서비스 미기동 시 BLOCKED( PASS 아님 ). | A `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/compose_check.py` services=['ai', 'back', 'db', 'front'] findings=0 | B `/Users/jeong-yelim/orca/pivotSeoul_v2/.venv/bin/python qa/tools/http_smoke.py` HTTP smoke reached=3 | 두 도구 PASS
