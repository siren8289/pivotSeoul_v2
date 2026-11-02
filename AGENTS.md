# 상시 작업 규칙 (QA·Security V3)

신규 기능, 수정, 유지보수, 버그 수정, 리팩터링, API·DB·UI·인프라·배포 변경마다 TC 추가/갱신과 자동 검증을 수행한다. 기준은 `qa-policy.md`다. 사용자가 매번 QA를 요청하지 않는다.

## 매 작업

1. 변경 파일·영향 기능·API·DB·화면을 확인하고 `qa/input/testcases.tsv`·`qa/config/test_map.json`과 매핑한다.
2. 신규 기능 TC는 **실행 전에** `qa/input/testcases.tsv`에 추가한다. 기존 TC는 보존하고 필요한 항목만 수정한다.
3. 코드를 수정하고 테스트·독립 검증 명령을 함께 둔다. 명령은 `test_map.json`에 등록한다.
4. 관련 TC를 스크립트로 실행한다: `python qa/run_qa.py --profile required --gate` (venv 우선). 개발 중에는 `--area` / `--section` / `--tc`.
5. 서로 다른 두 검증 경로를 실행하고 명령·결과·증거를 각각 기록한다. 미실행은 PASS가 아니다.
6. FAIL/RISK는 **코드 재수정 전에** `fail.md`/`risk.md`와 `results.tsv`에 선기록하고 사용자에게 알린다.
7. 결과는 `qa/results/{area}/{section}/{YYYY-MM-DD}/`에만 누적한다(파일: `test_sheet.xlsx`, `pass.md`, `fail.md`, `risk.md`, `results.tsv`). 루트 Excel은 `qa/master_test_sheet.xlsx` 하나. 이력은 `qa/history/execution_log.tsv`.
8. 수정 후 두 경로로 재검증한다. PR·배포 전 `--profile regression --gate`.
9. 보고: 신규·수정 TC 수, 영역별 실행, 도구별 상태, PASS/FAIL/BLOCKED/ERROR/NOT_RUN/SKIPPED, 미해결 RISK, RUN_ID·경로. 실행하지 않은 영역은 성공이라 하지 않는다.
10. Hook/CI가 실제로 검증되지 않았으면 “매 작업 자동화 완료”라고 주장하지 않는다.

## 완료 금지

- 필수 게이트 종료 코드 ≠ 0
- HIGH/CRITICAL + OPEN RISK
- 새 기능에 연결된 필수 TC 또는 두 검증 증거 없음
- 요구사항 불명확 → 추측하지 말고 RISK
- 코드 위치 미확인 → `UNKNOWN`

## 섹션 단위 반영

섹션이 여럿이면 섹션 끝날 때마다 커밋·푸시한다.

## 기존 CI

`.github/workflows/ci.yml`의 data/AI/Spring/front/compose + Semgrep + CodeQL + QA gate를 유지한다. 단일 CI job만으로 해당 영역 PASS를 기록하지 않는다.
