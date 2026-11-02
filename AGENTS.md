# 상시 작업 규칙

기능 추가, 수정, 유지보수, 버그 수정, 리팩터링, 배포 설정 변경은 사용자가 QA를 다시 말하지 않아도 아래를 적용한다. 기준은 `qa-policy.md`다.

## 매 작업

1. 요구사항, 변경 파일, 영향 범위를 분석한다.
2. `qa/input/testcases.tsv`와 `qa/master_test_sheet.tsv`의 기존 TC를 재사용하고, 필요할 때만 추가한다. 실행 이력은 삭제하지 않는다.
3. 코드를 수정한다.
4. 관련 검사를 스크립트로 실행한다. 필수 게이트는 `python qa/run_qa.py --profile required --gate`다. 가상환경이 있으면 그 인터프리터를 쓴다. 개발 중에는 `--area` / `--section` / `--tc`로 변경 기능만 돌린다.
5. 필수 TC는 서로 다른 도구 2개로 교차 검증한다. 미실행 검증은 PASS가 아니다.
6. 결과를 PASS / FAIL / RISK / NOT_RUN으로 나눈다.
7. 실행한 섹션만 `qa/results/{area}/{section}/{YYYY-MM-DD}/`에 누적한다. 날짜 폴더에는 `test_sheet.xlsx`, `pass.md`, `fail.md`, `risk.md`, `summary.tsv`만 둔다. 최상단 마스터는 `qa/master_test_sheet.tsv` 하나다(전체 Excel 중복 금지). 파일·폴더명은 영어 snake_case, 보고서 본문은 한국어다.
8. FAIL 또는 RISK는 코드를 고치기 전에 `fail.md` 또는 `risk.md`에 먼저 적고 사용자에게 알린다.
9. 수정 후 두 도구로 재검증한다. PR·배포 전에는 `python qa/run_qa.py --profile regression --gate`를 실행한다.
10. 최종 결과(전체 TC 수, PASS/FAIL/RISK/NOT_RUN, 1·2차 검증, 실패 원인, 추가 필요 항목, 실행 일시·코드 위치)를 보고한다. 실행하지 않은 영역은 성공이라고 말하지 않는다.

## 완료 금지

- 필수 게이트가 0이 아니면 완료나 병합 가능으로 보고하지 않는다.
- `HIGH` 또는 `CRITICAL`이면서 `OPEN`인 위험이 있으면 완료나 병합 가능으로 보고하지 않는다.
- 요구사항이 불명확하면 동작을 추측하지 않고 RISK로 남긴다.
- 코드 위치는 확인한 값만 적고, 모르면 `UNKNOWN`이다.

## 섹션 단위 반영

한 작업 안에 섹션이 여럿이면 섹션이 끝날 때마다 커밋하고 푸시한다.

## 기존 검사

`.github/workflows/ci.yml`의 data, AI, Spring, front build, compose 작업은 유지한다. 그 작업 하나만으로 해당 테스트 종류를 PASS로 기록하지 않는다.
