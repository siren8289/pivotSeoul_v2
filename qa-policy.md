# QA·Security 정책

이 문서가 테스트 설계, 교차 검증, 기록 형식, 완료 조건의 기준이다. `AGENTS.md`는 매 작업에서 이 정책을 실행하도록 지시한다. 기록 항목의 이름과 상태 값은 이 파일을 따른다.

적용 범위는 최초 개발, 기능 추가, 수정, 유지보수, 버그 수정, 리팩터링, 배포 설정 변경이다. 사용자는 매번 QA를 요청하지 않는다.

## 1. 테스트 설계

- 프로젝트 구조, 기술 스택, 요구사항, 변경 영향 범위를 먼저 분석한다.
- ISTQB 테스트 설계 기법과 OWASP ASVS/WSTG, 그리고 해당 기술 공식 문서를 기준으로 TC를 설계한다.
- 정상값, 예외값, NULL, 빈 값, 경계값, 중복, 오류 응답, 권한, 보안, 회귀를 검토한다.
- 기존 TC는 재사용하고, 없는 경우만 추가한다. 기존 TC와 실행 이력은 삭제하지 않는다.
- 요구사항이 불명확하면 동작을 추측하지 않고 RISK로 기록한다.

## 2. 교차 테스트

- 코드 변경 직후 관련 검사를 실행한다.
- 기능 완료 전 서로 다른 도구 최소 2개로 교차 검증한다.
- 각 도구의 검증 범위, 실행 명령, 결과를 비교한다.
- 도구 하나의 필수 검사가 실패하면 완료로 처리하지 않는다.
- 미실행, 도구 오류, 검증 누락은 PASS가 아니다.
- 수정 뒤에는 두 도구로 다시 검증하고 회귀 검사를 실행한다.

필수 게이트 명령:

```bash
python qa/run_qa.py --profile required --gate
```

로컬 가상환경이 있으면 그 인터프리터로 실행한다.

| TC_ID | 종류 | 도구 A | 도구 B | 범위 |
| --- | --- | --- | --- | --- |
| QA-UNIT-DATA-001 | unit | pytest `data/tests` | `qa/tools/invariant_check.py` | 전처리 월 환산 주거비, NULL, 빈 주소 |
| QA-UNIT-RECORD-001 | unit | pytest `qa/tests` | `qa/tools/record_selfcheck.py` | 기록 추가, PASS 조건, 게이트 |
| QA-SEC-SECRET-001 | security | `qa/tools/secret_scan.py` | `qa/tools/secret_grep.py` | 추적 파일의 고신뢰 비밀값 패턴 |
| QA-SEC-AUTH-001 | security | `qa/tools/auth_surface.py` | `qa/tools/auth_grep.py` | 인증 없는 API 표면. 발견 시 RISK |

`/health`는 상태 확인용 공개 경로로 인증 표면 결함에서 제외한다. 진단·추천·RAG API는 제외하지 않는다.

기존 GitHub Actions 작업(data pytest, AI pytest, Spring test, front build, compose config)은 유지한다. 그 작업만으로 해당 종류를 PASS로 기록하지 않는다. AI pytest와 Spring test는 각각 도구가 하나이므로, 두 번째 도구 없이 api PASS로 적지 않는다.

프론트 `package.json`에는 test 스크립트가 없다. 프론트 unit/e2e는 실행 전까지 NOT_RUN이며 PASS로 적지 않는다.

## 3. 기록 위치

실행한 종류만 폴더를 만든다.

`qa/reports/{test-type}/{YYYY-MM-DD}/`

종류: `api`, `unit`, `integration`, `e2e`, `security`, `performance`, `regression`.

각 날짜 폴더의 파일:

- `pass.md`: 통과 TC의 목적, 도구, 기대·실제 결과
- `fail.md`: 실패 원인, 재현, 디버깅, 수정, 재검증
- `risk.md`: 잠재 위험, 예외 처리 누락, 보안 문제, 권장 조치, 처리 이력
- `results.tsv`: 해당 실행의 TC 상태

날짜는 Asia/Seoul이다. 같은 날 다시 실행하면 `RUN_ID`로 누적한다. 과거 기록은 삭제하거나 덮어쓰지 않는다.

## 4. 공통 항목

`results.tsv` 헤더:

`RUN_ID`, `TC_ID`, `실행시각`, `기능명`, `테스트종류`, `도구A`, `도구A결과`, `도구B`, `도구B결과`, `최종상태`, `GitCommit`, `파일`, `함수`, `줄번호`, `ISSUE_ID`, `RISK_ID`, `비고`

- 실행시각 형식: `YYYY-MM-DDTHH:MM:SS+09:00`
- 최종상태: `PASS`, `FAIL`, `BLOCKED`, `ERROR`, `NOT_RUN`, `SKIPPED`
- 도구 결과도 같은 상태 값을 쓴다.
- 최종상태 `PASS`는 두 도구 결과가 모두 `PASS`일 때만 허용한다.
- 코드 위치는 실행 시 확인한 값만 적는다. 확인하지 못하면 `UNKNOWN`.
- TSV는 UTF-8 BOM으로 저장한다.
- `ISSUE_ID`와 `RISK_ID`가 없으면 빈 칸이다.

`RUN_ID` 형식: `R{YYYYMMDD}-{HHMMSS}-{4 hex}`.

## 5. PASS / FAIL / RISK

**PASS:** 검증 목적, 사용 도구와 명령, 기대 결과, 실제 결과, 파일·함수·줄을 적는다.

**FAIL:** 입력값, 오류 메시지, 재현 방법, 기대·실제 결과, 오류 파일·함수·줄, 원인, 수정 위치, 재검증을 적는다.

**RISK:** 테스트 통과와 별도로 적는다. 심각도(`LOW`/`MEDIUM`/`HIGH`/`CRITICAL`), 발생 가능성, 영향, 권장 조치, 처리 상태(`OPEN`/`CLOSED`/`ACCEPTED`)를 적는다.

FAIL 또는 RISK를 발견하면 코드를 고치기 전에 MD에 먼저 적고 사용자에게 보고한다.

미해결 `HIGH`/`CRITICAL`이고 처리 상태가 `OPEN`인 위험은 완료와 병합을 막는다. 같은 `RISK_ID`의 최신 기록만 현재 상태로 본다. `ACCEPTED`는 사람이 근거를 남긴 수용이며, 자동으로 넣지 않는다.

## 6. 매 작업 절차

1. 요구사항, 변경 파일, 영향 범위를 분석한다.
2. 기존 TC를 확인하고 필요할 때만 추가한다.
3. 코드를 작성하거나 수정한다.
4. 관련 QA·Security 검사를 실행한다.
5. 최소 2개 도구로 교차 검증한다.
6. PASS / FAIL / RISK로 분류한다.
7. 날짜별 MD·TSV에 누적 기록한다.
8. 실패하면 원인을 분석하고 수정한 뒤 두 도구로 재검증한다.
9. 회귀 검사가 필요하면 `--profile regression`을 실행한다.
10. 최종 결과와 미해결 위험을 보고한다. 실행하지 않은 종류는 성공으로 보고하지 않는다.

## 7. 게이트

`python qa/run_qa.py --profile required --gate`는 다음이면 종료 코드 1이다.

- 필수 TC의 최신 최종상태가 `PASS`가 아님
- 최신 위험이 `HIGH` 또는 `CRITICAL`이면서 `OPEN`

필수 TC: `QA-UNIT-DATA-001`, `QA-UNIT-RECORD-001`, `QA-SEC-SECRET-001`, `QA-SEC-AUTH-001`.

CI는 이 명령을 실행하고, 실패하면 워크플로를 실패시킨다. 기존 검사 작업은 그대로 둔다.

## 8. 자동화 구성

- 실행기: `qa/run_qa.py`
- 기록기: `qa/record.py`
- 게이트: `qa/gate.py`
- 도구: `qa/tools/`
- 상시 절차: `.grok/skills/qa-automation/SKILL.md`
- 코드 변경 후 미실행을 막는 Stop hook: `.grok/hooks/qa-stop.json`

의존성: 필수 게이트의 data 검사는 `data/requirements.txt` (pytest, pandas, python-dotenv, requests). 기록기와 보안 도구는 Python 표준 라이브러리만 사용한다.
