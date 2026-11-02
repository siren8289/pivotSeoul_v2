# QA·Security 정책

이 문서가 테스트 설계, 교차 검증, 기록 형식, 완료 조건의 기준이다. `AGENTS.md`는 매 작업에서 이 정책을 실행하도록 지시한다.

적용 범위는 최초 개발, 기능 추가, 수정, 유지보수, 버그 수정, 리팩터링, 배포 설정 변경이다. 사용자는 매번 QA를 요청하지 않는다.

## 1. QA 테스트 영역

QA는 다음 4개 영역으로 고정한다.

1. 단위·통합 테스트 (`01_unit_integration`)
2. 웹·API 테스트 (`02_web_api`)
3. 보안·품질 검사 (`03_security_quality`)
4. 인프라·배포 검사 (`04_infra_deploy`)

## 2. 파일 및 폴더 명명 규칙

- 모든 파일명과 폴더명은 영어로 작성한다. 한글 파일·폴더명은 사용하지 않는다.
- 폴더·파일명은 소문자 `snake_case`를 권장한다.
- 기능별 섹션명도 영어다. 예: `data_transform`, `diagnosis_api`, `deploy_ci`
- 날짜 폴더는 `YYYY-MM-DD` 형식이다.
- Excel 시트 이름과 TC ID는 영어로 작성한다.
- 테스트 설명, 예상 결과, 오류 분석, 보고서 본문은 한국어로 작성한다.
- 코드 변수명, 명령어, 설정 키 등 기술 식별자는 영어로 유지한다.

## 3. QA 폴더 구조

```
qa/
├── master_test_sheet.tsv
├── input/
│   └── testcases.tsv
└── results/
    ├── 01_unit_integration/
    ├── 02_web_api/
    ├── 03_security_quality/
    └── 04_infra_deploy/
```

각 영역 아래 기능별 섹션 폴더를 두고, 날짜별로 결과를 저장한다.

```
qa/results/{area}/{section}/{YYYY-MM-DD}/
├── test_sheet.xlsx
├── pass.md
├── fail.md
├── risk.md
└── summary.tsv
```

`qa/master_test_sheet.tsv`가 전체 영역·섹션 TC 현황을 통합 관리한다. 최상단에 전체 현황 Excel을 중복 생성하지 않는다.

카탈로그 원본은 `qa/input/testcases.tsv`다.

## 4. 이중 테스트 규칙

- 모든 TC는 가능한 한 서로 다른 두 검증 방법으로 테스트한다.
- 두 검증은 서로 다른 관점이나 계층에서 동작을 확인해야 한다.
- 각 TC의 1차·2차 실행 명령, 예상 결과, 실제 결과를 각각 기록한다.
- 두 검증 모두 통과한 경우에만 최종 PASS다.
- 하나라도 실패하면 FAIL이다.
- 검증 불가·미실행은 RISK 또는 NOT_RUN으로 구분한다.
- 실행하지 않은 테스트를 PASS로 기록하지 않는다.

필수 게이트:

```bash
python qa/run_qa.py --profile required --gate
```

개발 중 관련 TC만: `--area` / `--section` / `--tc`  
PR·배포 전: `--profile regression --gate`

| TC_ID | area | section | tool A | tool B |
| --- | --- | --- | --- | --- |
| QA-UNIT-DATA-001 | 01_unit_integration | data_transform | pytest `data/tests` | `qa/tools/invariant_check.py` |
| QA-UNIT-RECORD-001 | 01_unit_integration | qa_recorder | pytest `qa/tests` | `qa/tools/record_selfcheck.py` |
| QA-UNIT-FRONT-001 | 02_web_api | common_ui | `node --test front/tests/front_unit.test.mjs` | `qa/tools/front_check.py` |
| QA-INT-PIPELINE-001 | 01_unit_integration | db_persist | pytest `qa/tests/test_integration_pipeline.py` | `qa/tools/integration_check.py` |
| QA-API-CONTRACT-001 | 02_web_api | diagnosis_api | pytest `qa/tests/test_api_contract.py` | `qa/tools/api_contract_check.py` |
| QA-E2E-FLOW-001 | 02_web_api | diagnosis_input | `node --test front/tests/e2e_flow.test.mjs` | `qa/tools/e2e_flow_check.py` |
| QA-SEC-SECRET-001 | 03_security_quality | nonfunctional_qa | `qa/tools/secret_scan.py` | `qa/tools/secret_grep.py` |
| QA-SEC-AUTH-001 | 03_security_quality | nonfunctional_qa | `qa/tools/auth_surface.py` | `qa/tools/auth_grep.py` |
| QA-PERF-BENCH-001 | 03_security_quality | nonfunctional_qa | pytest `qa/tests/test_performance.py` | `qa/tools/perf_benchmark.py` |
| QA-INFRA-COMPOSE-001 | 04_infra_deploy | deploy_ci | `qa/tools/compose_check.py` | `qa/tools/compose_grep.py` |

`/health`는 인증 표면 결함에서 제외한다. 진단·추천·RAG API는 제외하지 않는다.

기존 GitHub Actions 작업(data/AI/Spring/front/compose)은 유지한다. 그 작업만으로 PASS 기록하지 않는다.

## 5. 자동화 및 AI 토큰 절약

- QA Agent 1개와 QA Skill 1개(`.grok/skills/qa-automation`)를 사용한다.
- 신규 TC 작성, 변경 영향 분석, 복잡한 실패 원인 분석에만 AI를 사용한다.
- 기존 테스트 실행과 결과 판정은 `qa/run_qa.py` 등 스크립트로 처리한다.
- 테스트 실행 시 전체 프로젝트와 TSV를 매번 AI에 전달하지 않는다.
- TC를 순차 실행하고 결과 시트를 갱신한다.
- Excel·Markdown 보고서 생성은 AI 호출 없이 수행한다.

## 6. 기록 형식

`summary.tsv` 헤더(영어):

`RUN_ID`, `TC_ID`, `executed_at`, `area`, `section`, `feature`, `test_type`, `tool_a`, `tool_a_result`, `tool_b`, `tool_b_result`, `final_status`, `git_commit`, `file`, `function`, `line`, `issue_id`, `risk_id`, `note`

- `executed_at`: `YYYY-MM-DDTHH:MM:SS+09:00` (Asia/Seoul)
- `final_status`: `PASS`, `FAIL`, `BLOCKED`, `ERROR`, `NOT_RUN`, `SKIPPED`, `RISK`
- `PASS`는 두 도구 결과가 모두 `PASS`일 때만 허용한다.
- 코드 위치는 확인한 값만 적고, 모르면 `UNKNOWN`
- TSV는 UTF-8 BOM
- `RUN_ID`: `R{YYYYMMDD}-{HHMMSS}-{4 hex}`
- 같은 날 재실행은 `RUN_ID`로 누적. 과거 기록은 덮어쓰지 않는다.

`pass.md` / `fail.md` / `risk.md` 본문은 한국어다.

## 7. PASS / FAIL / RISK

**PASS:** 검증 목적, 도구·명령, 기대·실제, 파일·함수·줄  
**FAIL:** 입력, 오류, 재현, 기대·실제, 원인, 수정 위치, 재검증  
**RISK:** 심각도(`LOW`/`MEDIUM`/`HIGH`/`CRITICAL`), 발생 가능성, 영향, 권장 조치, 처리 상태(`OPEN`/`CLOSED`/`ACCEPTED`)

FAIL·RISK는 코드 수정 전에 MD에 먼저 적고 사용자에게 보고한다.  
`HIGH`/`CRITICAL` + `OPEN`이면 완료·병합을 막는다. `ACCEPTED`는 사람만 기록한다.

## 8. 지속적인 QC

- 신규 기능 개발 시 해당 기능 TC를 추가한다.
- 기능 수정 시 연결된 TC를 재실행한다.
- 실패 TC 수정 후 관련 회귀를 수행한다.
- PR·배포 전 전체 회귀를 실행한다.
- 필수 테스트 실패 시 CI에서 병합·배포를 차단한다.
- 실행 결과와 이력을 보존한다.

## 9. 최종 보고

테스트 종료 후 기록한다.

- 전체 TC 수
- PASS / FAIL / RISK / NOT_RUN
- 1차·2차 검증 결과
- 실패 원인과 재현 절차
- 추가 테스트가 필요한 항목
- 실행 일시 및 관련 코드 위치

본문은 한국어, 파일·폴더·기술 식별자는 영어다.

## 10. 게이트

`python qa/run_qa.py --profile required --gate`는 다음이면 종료 코드 1이다.

- 필수 TC 최신 `final_status`가 `PASS`가 아님
- 최신 위험이 `HIGH`/`CRITICAL`이면서 `OPEN`

필수 TC: `QA-UNIT-DATA-001`, `QA-UNIT-RECORD-001`, `QA-UNIT-FRONT-001`, `QA-INT-PIPELINE-001`, `QA-API-CONTRACT-001`, `QA-E2E-FLOW-001`, `QA-SEC-SECRET-001`, `QA-SEC-AUTH-001`, `QA-PERF-BENCH-001`, `QA-INFRA-COMPOSE-001`

## 11. 자동화 구성

- 실행기: `qa/run_qa.py`
- 기록기: `qa/record.py`
- 시트: `qa/sheet.py` (날짜 `test_sheet.xlsx`만)
- 게이트: `qa/gate.py`
- 입력: `qa/input/testcases.tsv`
- 마스터: `qa/master_test_sheet.tsv`
- 도구: `qa/tools/`
- Skill: `.grok/skills/qa-automation/SKILL.md`
- Stop hook: `.grok/hooks/qa-stop.json`
