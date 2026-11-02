# 상시 작업 규칙

기능 추가, 수정, 유지보수, 버그 수정, 리팩터링, 배포 설정 변경은 사용자가 QA를 다시 말하지 않아도 아래를 적용한다. 테스트 설계, 기록 형식, 상태 값, 필수 TC의 기준은 `qa-policy.md`이다.

## 매 작업

1. 요구사항, 변경 파일, 영향 범위를 분석한다.
2. `docs/qa/`의 기존 TC를 재사용하고, 필요할 때만 추가한다. 기존 TC와 `qa/reports` 이력은 삭제하지 않는다.
3. 코드를 수정한다.
4. 관련 검사를 실행한다. 필수 게이트는 `python qa/run_qa.py --profile required --gate` 이다. 가상환경이 있으면 그 인터프리터를 쓴다.
5. 필수 TC는 서로 다른 도구 2개로 교차 검증한다. 도구, 명령, 범위를 `qa-policy.md`의 표와 맞춘다.
6. 결과를 PASS / FAIL / RISK로 나눈다. 미실행, 도구 오류, 검증 누락은 PASS가 아니다.
7. 실행한 종류만 `qa/reports/{test-type}/{YYYY-MM-DD}/`에 누적한다. 날짜는 Asia/Seoul이다. 같은 날이라도 `RUN_ID`로 추가하고 과거 기록을 덮어쓰지 않는다.
8. FAIL 또는 RISK는 코드를 고치기 전에 `fail.md` 또는 `risk.md`에 먼저 적고 사용자에게 알린다.
9. 수정 후 두 도구로 재검증한다. 회귀가 필요하면 `python qa/run_qa.py --profile regression --gate`를 실행한다.
10. 최종 결과와 미해결 위험을 보고한다. 실행하지 않은 api, integration, e2e, performance는 성공이라고 말하지 않는다.

## 완료 금지

- 필수 게이트가 0이 아니면 완료나 병합 가능으로 보고하지 않는다.
- `HIGH` 또는 `CRITICAL`이면서 `OPEN`인 위험이 있으면 완료나 병합 가능으로 보고하지 않는다.
- 요구사항이 불명확하면 동작을 추측하지 않고 RISK로 남긴다.
- 코드 위치는 확인한 값만 적고, 모르면 `UNKNOWN`이다.

## 섹션 단위 반영

한 작업 안에 섹션이 여럿이면 섹션이 끝날 때마다 커밋하고 푸시한다.

## 기존 검사

`.github/workflows/ci.yml`의 data, AI, Spring, front build, compose 작업은 유지한다. 그 작업 하나만으로 해당 테스트 종류를 PASS로 기록하지 않는다.
