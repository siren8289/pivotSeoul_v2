# RISK

잠재 위험. 같은 RISK_ID의 마지막 처리상태가 현재 상태다.

## R20261102-201603-7ca2 RISK-SEC-001

- RISK_ID: RISK-SEC-001
- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-02T20:16:03+09:00
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

## R20261102-201603-7ca2 RISK-QA-001

- RISK_ID: RISK-QA-001
- TC_ID: QA-UNIT-FRONT-001
- 실행시각: 2026-11-02T20:16:03+09:00
- 심각도: MEDIUM
- 발생가능성: HIGH
- 영향: 화면 변경의 회귀를 자동 테스트로 확인하지 못한다.
- 처리상태: OPEN
- 권장조치: 프론트 테스트 도구를 정한 뒤 unit 또는 e2e를 두 도구로 실행한다. 도구는 아직 정하지 않았다.
- 파일: front/package.json
- 함수: UNKNOWN
- 줄번호: 6
- ISSUE_ID: 
- 근거: front/package.json에 test 스크립트가 없다. 프론트 테스트는 실행하지 않았다.

## R20261102-222811-3229 RISK-SEC-001

- RISK_ID: RISK-SEC-001
- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-02T22:28:11+09:00
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

## R20261102-222811-3229 RISK-QA-001

- RISK_ID: RISK-QA-001
- TC_ID: QA-UNIT-FRONT-001
- 실행시각: 2026-11-02T22:28:11+09:00
- 심각도: MEDIUM
- 발생가능성: HIGH
- 영향: 화면 변경의 회귀를 자동 테스트로 확인하지 못한다.
- 처리상태: OPEN
- 권장조치: 프론트 테스트 도구를 정한 뒤 unit 또는 e2e를 두 도구로 실행한다. 도구는 아직 정하지 않았다.
- 파일: front/package.json
- 함수: UNKNOWN
- 줄번호: 6
- ISSUE_ID: 
- 근거: front/package.json에 test 스크립트가 없다. 프론트 테스트는 실행하지 않았다.

## R20261102-225315-2e02 RISK-QA-001

- RISK_ID: RISK-QA-001
- TC_ID: QA-UNIT-FRONT-001
- 실행시각: 2026-11-02T22:53:15+09:00
- 심각도: MEDIUM
- 발생가능성: LOW
- 영향: front/package.json에 test 스크립트를 구성하고 node --test와 front_check.py 두 도구로 교차 검증을 완료했다.
- 처리상태: CLOSED
- 권장조치: 완료 (2개 도구 교차 검증 상시 실행).
- 파일: front/package.json
- 함수: DISTRICTS
- 줄번호: 10
- ISSUE_ID: 
- 근거: node --test front/tests/front_unit.test.mjs 및 qa/tools/front_check.py 모두 PASS.

## R20261102-225315-2e02 RISK-SEC-001

- RISK_ID: RISK-SEC-001
- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-02T22:53:15+09:00
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

## R20261102-225405-4684 RISK-QA-001

- RISK_ID: RISK-QA-001
- TC_ID: QA-UNIT-FRONT-001
- 실행시각: 2026-11-02T22:54:05+09:00
- 심각도: MEDIUM
- 발생가능성: LOW
- 영향: front/package.json에 test 스크립트를 구성하고 node --test와 front_check.py 두 도구로 교차 검증을 완료했다.
- 처리상태: CLOSED
- 권장조치: 완료 (2개 도구 교차 검증 상시 실행).
- 파일: front/package.json
- 함수: DISTRICTS
- 줄번호: 10
- ISSUE_ID: 
- 근거: node --test front/tests/front_unit.test.mjs 및 qa/tools/front_check.py 모두 PASS.

## R20261102-225405-4684 RISK-SEC-001

- RISK_ID: RISK-SEC-001
- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-02T22:54:05+09:00
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
