# RISK

잠재 위험. 같은 RISK_ID의 마지막 처리상태가 현재 상태다.

## R20261103-015624-f1a2 RISK-SEC-001

- RISK_ID: RISK-SEC-001
- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-03T01:56:24+09:00
- 심각도: HIGH
- 발생가능성: HIGH
- 영향: 진단·추천·RAG API에 인증 표시가 없다. Diagnosis.monthlyIncome은 저장되고 id는 IDENTITY로 증가한다. 권한 정책은 확정되어 있지 않아 결함으로 단정하지 않는다.
- 처리상태: OPEN
- 권장조치: 접근 정책을 정하기 전에는 완료로 보지 않는다. 인증을 넣거나, 공개 범위와 식별자 정책을 정한 뒤 ACCEPTED로 남긴다.
- 파일: back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java
- 함수: get
- 줄번호: 39
- ISSUE_ID: 
- 근거: 두 도구의 매핑 목록이 같다. /health 는 제외했다. monthlyIncome 줄 32, @GeneratedValue 줄 22. 목록: ai/src/api/main.py:56, ai/src/api/main.py:61, ai/src/features/housing_rag_001/router.py:51, ai/src/features/housing_rag_001/router.py:58, ai/src/features/housing_rag_001/router.py:80, ai/src/features/housing_rag_001/router.py:99, ai/src/features/housing_rag_001/router.py:154, back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java:24, back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java:33, back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java:39, back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java:44, back/src/main/java/com/pivotseoul/recommend/controller/RecommendController.java:16, back/src/main/java/com/pivotseoul/recommend/controller/RecommendController.java:25

## R20261103-025113-52fb RISK-SEC-001

- RISK_ID: RISK-SEC-001
- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-03T02:51:13+09:00
- 심각도: HIGH
- 발생가능성: HIGH
- 영향: 진단·추천·RAG API에 인증 표시가 없다.
- 처리상태: OPEN
- 권장조치: 접근 정책 확정 전 완료로 보지 않는다.
- 파일: back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java
- 함수: get
- 줄번호: 39
- ISSUE_ID: 
- 근거: 목록=ai/src/api/main.py:56, ai/src/api/main.py:61, ai/src/features/housing_rag_001/router.py:51, ai/src/features/housing_rag_001/router.py:58, ai/src/features/housing_rag_001/router.py:80, ai/src/features/housing_rag_001/router.py:99, ai/src/features/housing_rag_001/router.py:154, back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java:24, back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java:33, back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java:39, back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java:44, back/src/main/java/com/pivotseoul/recommend/controller/RecommendController.java:16, back/src/main/java/com/pivotseoul/recommend/controller/RecommendController.java:25

## R20261103-025113-52fb RISK-V3-CODEQL

- RISK_ID: RISK-V3-CODEQL
- TC_ID: QA-SEC-SEMGREP-001
- 실행시각: 2026-11-03T02:51:13+09:00
- 심각도: MEDIUM
- 발생가능성: LOW
- 영향: 로컬 2차는 secret-grep이다. CodeQL은 GitHub Actions codeql job이 공식 병행 경로다.
- 처리상태: OPEN
- 권장조치: CI CodeQL required check를 브랜치 보호에 포함한다.
- 파일: .github/workflows/ci.yml
- 함수: UNKNOWN
- 줄번호: UNKNOWN
- ISSUE_ID: 
- 근거: V3 03_security_quality CodeQL+Semgrep

## R20261103-040333-4843 RISK-SEC-001

- RISK_ID: RISK-SEC-001
- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-03T04:03:33+09:00
- 심각도: HIGH
- 발생가능성: HIGH
- 영향: 진단·추천·RAG API에 인증 표시가 없다.
- 처리상태: OPEN
- 권장조치: 접근 정책 확정 전 완료로 보지 않는다.
- 파일: back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java
- 함수: get
- 줄번호: 39
- ISSUE_ID: 
- 근거: 목록=ai/src/api/main.py:56, ai/src/api/main.py:61, ai/src/features/housing_rag_001/router.py:51, ai/src/features/housing_rag_001/router.py:58, ai/src/features/housing_rag_001/router.py:80, ai/src/features/housing_rag_001/router.py:99, ai/src/features/housing_rag_001/router.py:154, back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java:24, back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java:33, back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java:39, back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java:44, back/src/main/java/com/pivotseoul/recommend/controller/RecommendController.java:16, back/src/main/java/com/pivotseoul/recommend/controller/RecommendController.java:25

## R20261103-040333-4843 RISK-V3-CODEQL

- RISK_ID: RISK-V3-CODEQL
- TC_ID: QA-SEC-SEMGREP-001
- 실행시각: 2026-11-03T04:03:33+09:00
- 심각도: MEDIUM
- 발생가능성: LOW
- 영향: 로컬 2차는 secret-grep이다. CodeQL은 GitHub Actions codeql job이 공식 병행 경로다.
- 처리상태: OPEN
- 권장조치: CI CodeQL required check를 브랜치 보호에 포함한다.
- 파일: .github/workflows/ci.yml
- 함수: UNKNOWN
- 줄번호: UNKNOWN
- ISSUE_ID: 
- 근거: V3 03_security_quality CodeQL+Semgrep

## R20261103-040333-4843 RISK-SHEET-NOT-MAPPED

- RISK_ID: RISK-SHEET-NOT-MAPPED
- TC_ID: SHEET-CATALOG
- 실행시각: 2026-11-03T04:03:33+09:00
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
