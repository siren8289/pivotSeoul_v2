# RISK

잠재 위험. 같은 RISK_ID의 마지막 처리상태가 현재 상태다.

## R20261102-201549-c42d RISK-QA-001

- RISK_ID: RISK-QA-001
- TC_ID: QA-UNIT-FRONT-001
- 실행시각: 2026-11-02T20:15:49+09:00
- 심각도: MEDIUM
- 발생가능성: HIGH
- 영향: 화면 변경의 회귀를 자동 테스트로 확인하지 못한다.
- 처리상태: OPEN
- 권장조치: 프론트 테스트 도구를 정한 뒤 unit 또는 e2e를 두 도구로 실행한다. 도구는 아직 정하지 않았다.
- 파일: front/package.json
- 함수: UNKNOWN
- 줄번호: 6
- ISSUE_ID: 
- 근거: front/package.json에 test 스크립트가 없다. 프론트 테스트는 실행하지 않았다.
