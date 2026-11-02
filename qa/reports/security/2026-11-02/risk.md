# RISK

잠재 위험. 같은 RISK_ID의 마지막 처리상태가 현재 상태다.

## R20261102-201549-c42d RISK-SEC-001

- RISK_ID: RISK-SEC-001
- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-02T20:15:49+09:00
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

## R20261102-222809-8f28 RISK-SEC-001

- RISK_ID: RISK-SEC-001
- TC_ID: QA-SEC-AUTH-001
- 실행시각: 2026-11-02T22:28:09+09:00
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
