# RISK

잠재 위험 등록부. 실행 상태와 별개이며 같은 RISK_ID의 마지막 처리상태가 현재 상태다.

## R20261103-035418-0890 RISK-SHEET-NOT-MAPPED

- RISK_ID: RISK-SHEET-NOT-MAPPED
- TC_ID: SHEET-CATALOG
- 실행시각: 2026-11-03T03:54:18+09:00
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
