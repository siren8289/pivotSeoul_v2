---
name: qa-automation
description: Run the pivotSeoul QA and security gate after every code, test, CI, or deploy change. Use when adding a feature, fixing a bug, refactoring, or editing Docker, compose, or GitHub Actions. Records qa/results/{area}/{section}/{date} and does not treat unrun checks as PASS.
---

# QA 자동화

기준은 `qa-policy.md`다. `AGENTS.md`의 완료 금지를 지킨다.

QA Agent 1개와 이 Skill 1개만 사용한다. 실행·판정·Excel/Markdown 생성은 스크립트로 하고, AI는 신규 TC·영향 분석·복잡 실패 분석에만 쓴다. 전체 프로젝트/TSV를 매번 AI에 넣지 않는다.

## 구조

```
qa/
├── master_test_sheet.tsv
├── input/testcases.tsv
└── results/
    ├── 01_unit_integration/
    ├── 02_web_api/
    ├── 03_security_quality/
    └── 04_infra_deploy/
```

날짜 폴더: `test_sheet.xlsx`, `pass.md`, `fail.md`, `risk.md`, `summary.tsv`  
파일·폴더·TC ID·시트명은 영어. 보고서 본문은 한국어. 최상단 전체 Excel은 만들지 않는다.

## 실행

```bash
python qa/run_qa.py --profile required --gate
```

개발 중:

```bash
python qa/run_qa.py --profile required --area 01_unit_integration --section data_transform
```

PR·배포 전:

```bash
python qa/run_qa.py --profile regression --gate
```

가상환경이 있으면 그 인터프리터를 쓴다.

## 완료 전

- 게이트 종료 코드가 0이 아니면 완료로 보고하지 않는다.
- `HIGH`/`CRITICAL` + `OPEN` 위험은 수정 전에 `risk.md`에 적고 사용자에게 알린다.
- 실행하지 않은 영역·섹션은 PASS라고 말하지 않는다.
- 기존 날짜 기록은 지우거나 덮어쓰지 않는다.
- 보고: 전체 TC 수, PASS/FAIL/RISK/NOT_RUN, 1·2차 검증, 실패 원인·재현, 추가 필요 항목, 일시·코드 위치.
