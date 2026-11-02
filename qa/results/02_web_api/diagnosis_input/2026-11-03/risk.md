# RISK

잠재 위험. 같은 RISK_ID의 마지막 처리상태가 현재 상태다.

## R20261103-025113-52fb RISK-V3-PLAYWRIGHT

- RISK_ID: RISK-V3-PLAYWRIGHT
- TC_ID: QA-E2E-FLOW-001
- 실행시각: 2026-11-03T02:51:13+09:00
- 심각도: MEDIUM
- 발생가능성: MEDIUM
- 영향: V3 목표 도구인 Playwright가 아직 기본 경로가 아니다. 현재는 node --test/E2E와 독립 Python 검증을 사용한다.
- 처리상태: OPEN
- 권장조치: Playwright 스모크를 front에 추가하고 test_map 1차 도구를 교체한다.
- 파일: front/package.json
- 함수: UNKNOWN
- 줄번호: UNKNOWN
- ISSUE_ID: 
- 근거: test_map.json 02_web_api note

## R20261103-035924-45a7 RISK-V3-PLAYWRIGHT

- RISK_ID: RISK-V3-PLAYWRIGHT
- TC_ID: QA-E2E-FLOW-001
- 실행시각: 2026-11-03T03:59:24+09:00
- 심각도: MEDIUM
- 발생가능성: MEDIUM
- 영향: V3 목표 도구인 Playwright가 아직 기본 경로가 아니다. 현재는 node --test/E2E와 독립 Python 검증을 사용한다.
- 처리상태: OPEN
- 권장조치: Playwright 스모크를 front에 추가하고 test_map 1차 도구를 교체한다.
- 파일: front/package.json
- 함수: UNKNOWN
- 줄번호: UNKNOWN
- ISSUE_ID: 
- 근거: test_map.json 02_web_api note

## R20261103-035924-45a7 RISK-SHEET-NOT-MAPPED

- RISK_ID: RISK-SHEET-NOT-MAPPED
- TC_ID: SHEET-CATALOG
- 실행시각: 2026-11-03T03:59:24+09:00
- 심각도: MEDIUM
- 발생가능성: HIGH
- 영향: 749 원자 TC 중 전용 이중 검증 명령이 없는 항목은 NOT_RUN이다. 관련 스위트 PASS를 개별 TC PASS로 대체하지 않는다.
- 처리상태: OPEN
- 권장조치: 우선순위 P0부터 test_map.json에 TOOL_A/B 명령을 연결한다.
- 파일: qa/input/testcases.tsv
- 함수: UNKNOWN
- 줄번호: UNKNOWN
- ISSUE_ID: 
- 근거: V3 정책 — 미실행 PASS 금지

## R20261103-040635-325a RISK-V3-PLAYWRIGHT

- RISK_ID: RISK-V3-PLAYWRIGHT
- TC_ID: QA-E2E-FLOW-001
- 실행시각: 2026-11-03T04:06:35+09:00
- 심각도: MEDIUM
- 발생가능성: MEDIUM
- 영향: V3 목표 도구인 Playwright가 아직 기본 경로가 아니다. 현재는 node --test/E2E와 독립 Python 검증을 사용한다.
- 처리상태: OPEN
- 권장조치: Playwright 스모크를 front에 추가하고 test_map 1차 도구를 교체한다.
- 파일: front/package.json
- 함수: UNKNOWN
- 줄번호: UNKNOWN
- ISSUE_ID: 
- 근거: test_map.json 02_web_api note
