---
name: qa-automation
description: Run the pivotSeoul QA and security gate after every code, test, CI, or deploy change. Use when adding a feature, fixing a bug, refactoring, or editing Docker, compose, or GitHub Actions. Records qa/reports and does not treat unrun checks as PASS.
---

# QA 자동화

기준은 `qa-policy.md`다. `AGENTS.md`의 완료 금지를 지킨다.

## 실행

코드, 테스트, CI, compose, 배포 스크립트를 바꾼 뒤 저장소 루트에서 실행한다.

```bash
python qa/run_qa.py --profile required --gate
```

가상환경이 있으면 그 인터프리터를 쓴다. 회귀가 필요하면 `--profile regression`으로 한 번 더 실행한다.

## 완료 전

- 게이트 종료 코드가 0이 아니면 완료로 보고하지 않는다.
- `HIGH` 또는 `CRITICAL`이면서 `OPEN`인 위험은 코드를 더 고치기 전에 `qa/reports/.../risk.md`에 적고 사용자에게 알린다.
- 실행하지 않은 테스트 종류가 있으면 그 종류 폴더를 만들지 않고 PASS라고 말하지 않는다.
- 기존 `qa/reports`와 `docs/qa` 기록은 지우거나 덮어쓰지 않는다.
