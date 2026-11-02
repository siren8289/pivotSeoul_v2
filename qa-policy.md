# QA·Security 정책 V3.0

이 문서가 테스트 설계, 교차 검증, 기록 형식, 완료 조건의 기준이다. `AGENTS.md`와 `.grok/skills/qa-automation/SKILL.md`가 매 작업에서 이 정책을 실행한다.

적용: 신규 기능, 수정, 유지보수, 버그 수정, 리팩터링, API·DB·UI·인프라·배포 설정 변경. 사용자가 매번 QA를 요청하지 않는다.

> 지침만 작성했다고 자동 실행되었다고 보고하지 않는다. 로컬 Hook과 GitHub Actions를 실제로 연결·검증한다.

## 1. 4개 영역과 이중 검증

| 영역 폴더 | 1차 검증 | 2차 검증 | 핵심 검증 |
| --- | --- | --- | --- |
| `01_unit_integration` | pytest / JUnit / Vitest(해당 스택) | 독립 블랙박스·계약 검증(필요 시 Testcontainers) | 함수 결과, 분기, 서비스·DB 연동 |
| `02_web_api` | Playwright(목표) / 현재 node E2E | OpenAPI·계약 검증(Schemathesis급) | UI 흐름, HTTP 상태·본문·오류·권한 |
| `03_security_quality` | Semgrep | CodeQL(CI) + 비밀/인가 이중 스캔 | 취약 패턴, 비밀·인가 누락 |
| `04_infra_deploy` | Compose 설정·구조 | curl HTTP 스모크(기동 시/회귀) | 컨테이너 준비, 실제 요청 |

명령 매핑의 SSOT는 `qa/config/test_map.json`이다. AI가 매 실행마다 명령을 추측하지 않는다.

- 같은 명령을 두 번 실행한 것은 교차 검증이 아니다.
- 필수 경로가 하나뿐이면 이유·대체 계획을 `risk.md`에 남기고 PASS로 처리하지 않는다.
- CodeQL·Semgrep은 UI/API/배포 실동작 검사를 대체하지 않는다. k6는 스테이징 등 격리 환경에서만.

## 2. TC 분해

변경된 파일과 연결된 기능부터 `요구사항 → 기능 → 화면/API → 서비스/함수 → DB/외부 → 예외/상태`를 갱신한다. 전체 프로젝트를 매번 AI 문맥에 넣지 않는다.

원자적 TC로 분해: 입력, 경계, 처리·분기, 출력, 상태·데이터, 인증·권한, 외부 장애, 보안·운영, 회귀. 제외 시 이유를 남긴다. 추측 금지 → `RISK`.

필수 필드: `TC_ID`, `FEATURE_ID`, `REQUIREMENT_ID`, `AREA`, `SECTION`, `SCENARIO`, `PRECONDITION`, `INPUT`, `STEPS`, `EXPECTED_RESULT`, `TOOL_A`, `COMMAND_A`, `TOOL_B`, `COMMAND_B`, `CODE_FILE`, `FUNCTION`, `RISK_LEVEL`(필요 시).

## 3. 완료 순서

1. 변경 전 매핑 2. 신규 TC를 실행 전 `qa/input/testcases.tsv`에 등록 3. 코드·테스트·명령 작성 4. 1·2차 즉시 실행·증거 수집 5. FAIL/RISK는 **수정 전** 선기록·사용자 알림 6. 재검증 7. 필수 TC·두 경로 증거 없으면 완료 금지 8. PR/배포 전 회귀·보안·배포 검증, CI 실패·HIGH/CRITICAL OPEN이면 병합 차단

## 4. 폴더·파일 (영어)

```
qa/
├── master_test_sheet.xlsx
├── input/testcases.tsv
├── config/test_map.json
├── history/execution_log.tsv
└── results/{area}/{section}/{YYYY-MM-DD}/
    ├── test_sheet.xlsx
    ├── pass.md
    ├── fail.md
    ├── risk.md
    └── results.tsv
```

- `master_test_sheet.xlsx`: qa 루트 유일 전체 현황 Excel
- `results.tsv`·`execution_log.tsv`: append-only, 잠금/원자 저장
- 설명·원인·보고서 본문: 한국어 / 이름·ID·컬럼: 영어 / 날짜: Asia/Seoul `YYYY-MM-DD`

## 5. 상태·증거·차단

실행 상태: `PASS / FAIL / BLOCKED / ERROR / NOT_RUN / SKIPPED`  
**RISK는 별도 등록부**(심각도·가능성·영향·조치·OPEN/CLOSED/ACCEPTED).

`PASS`는 두 필수 경로 실행 + 모든 필수 단언 통과 + 증거 존재. 미실행을 PASS로 쓰지 않는다. SKIPPED 필수는 PASS로 계산하지 않는다.

기록: `RUN_ID`, `TC_ID`, `FEATURE_ID`, 시작/종료(KST), 도구·명령, 각 결과, 최종 상태, 기대/실제, 증거 경로, Git SHA, 파일·함수·줄(`UNKNOWN` 가능), ISSUE/RISK ID. 비밀·토큰·개인정보 금지.

필수 게이트:

```bash
python qa/run_qa.py --profile required --gate
```

개발: `--area` / `--section` / `--tc`  
PR·배포: `--profile regression --gate` (HTTP 스모크 포함)

## 6. 자동화·토큰

- QA Agent 1 + Skill 1
- 실행·판정·리포트·Excel은 스크립트
- 로컬 Stop hook: `.grok/hooks/qa-stop.json` → `qa/hooks/stop_qa.py`
- CI: push/PR 시 data/ai/back/front/compose + Semgrep + CodeQL + QA gate
- AI는 TC 설계·복잡 영향·원인 불명 분석에만

## 7. 보고·완료 조건

보고(한국어): 변경 기능, 신규·수정 TC 수, 영역별 실행, 도구별 상태, PASS/FAIL/BLOCKED/ERROR/NOT_RUN/SKIPPED, 미해결 RISK, 경로·RUN_ID.

기능 완료: (1) TC 등록 (2) 테스트 코드·명령 연결 (3) 두 경로 증거 (4) 필수 통과 (5) 5개 결과 파일+master Excel (6) HIGH/CRITICAL OPEN 없음. 미달 시 미완료.

## 8. 근거

ISTQB CTFL, OWASP ASVS/WSTG, pytest, Playwright, Compose readiness, GitHub Actions/protected branches, k6 thresholds. 본 문서는 프로젝트 맞춤 운영정책이다.
