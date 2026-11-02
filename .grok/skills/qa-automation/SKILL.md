---
name: qa-automation
description: Run pivotSeoul QA·Security V3 after every code, test, CI, or deploy change. Dual-tool checks via qa/config/test_map.json; records qa/results and master_test_sheet.xlsx; never treat unrun checks as PASS.
---

# QA 자동화 V3

기준: `qa-policy.md`, `AGENTS.md`. Agent 1 + 이 Skill 1만 사용한다.

실행·판정·Excel/Markdown은 스크립트. AI는 신규 TC·복잡 영향·원인 불명 FAIL/RISK에만. 전체 코드/TSV를 매번 문맥에 넣지 않는다.

## 구조

```
qa/
├── master_test_sheet.xlsx
├── input/testcases.tsv
├── config/test_map.json
├── history/execution_log.tsv
└── results/{01_unit_integration|02_web_api|03_security_quality|04_infra_deploy}/{section}/{YYYY-MM-DD}/
```

날짜 폴더: `test_sheet.xlsx`, `pass.md`, `fail.md`, `risk.md`, `results.tsv`

## 실행

```bash
python qa/run_qa.py --profile required --gate
python qa/run_qa.py --profile required --area 01_unit_integration --section data_transform
python qa/run_qa.py --profile regression --gate
```

venv가 있으면 그 인터프리터를 쓴다. 명령은 `qa/config/test_map.json`에서 읽는다.

## Hook / CI

- 로컬 Stop: `.grok/hooks/qa-stop.json` → `python qa/hooks/stop_qa.py`
- CI: push/PR → data/ai/back/front/compose + Semgrep + CodeQL + QA gate

연결·작동을 확인하기 전에는 “자동화 완료”라고 보고하지 않는다.

## 완료 전

- 게이트 ≠ 0 이면 완료 금지
- HIGH/CRITICAL OPEN 선기록·사용자 알림
- 미실행 영역 PASS 금지
- 이력 삭제/덮어쓰기 금지
- 보고: TC 수, 상태 집계, 1·2차 결과, RISK, RUN_ID·경로
