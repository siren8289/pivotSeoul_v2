# pivotSeoul — PostgreSQL 성능 최적화 및 데이터 파이프라인 효율화

> **시뮬레이션 결과 조회의 N+1 가능성을 JOIN 1회로 고정하고, PostgreSQL 실행계획 기반 인덱스 최적화와 스키마 슬림화, Partial Index·BRIN·RANGE Partitioning, Star Schema·Materialized View·증분 ETL·CDC-lite·Airflow/Spark까지 적용한 DB/DE 프로젝트**

* **프로젝트 구분:** 개인 프로젝트
* **핵심 역할:** PostgreSQL Schema/Index 설계, Query Optimization, DB Monitoring, Data Modeling, Incremental ETL, Data Quality, Pipeline Orchestration
* **기술 스택:** PostgreSQL, Spring Boot, Spring Data JPA, Flyway, Micrometer, Prometheus, Python, Apache Airflow, Apache Spark, Docker
* **주요 영역:** DBA / Database Performance Engineering / Data Engineering

---

# 1. 문제 상황 및 요구사항

## 1-1. 프로젝트 배경

pivotSeoul은 사용자의 소득·보증금·월세 등의 조건을 기반으로 주거비 부담 시뮬레이션을 실행하고, 시뮬레이션 결과와 임계값 판단을 제공하는 서비스입니다.

핵심 데이터 흐름은 다음과 같습니다.

```text
사용자 조건 입력
→ Simulation Session 생성
→ Scenario 생성
→ Simulation Run 실행
→ Scenario Result 저장
→ Threshold Result 판단
→ 결과 API 조회
```

서비스 기능을 구현하는 과정에서 DB와 데이터 처리 구조에 네 가지 문제가 있었습니다.

첫째, 결과 조회 API에서 `scenario_result`와 여러 개의 `threshold_result`를 함께 조회해야 했기 때문에 JPA Lazy Loading을 그대로 사용할 경우 결과 건수에 따라 SQL 수가 증가하는 N+1 문제가 발생할 가능성이 있었습니다.

둘째, MVP에서 실제로 사용하지 않는 테이블과 컬럼이 다수 남아 있어 Entity, DTO, API, 테스트와 DB 스키마의 관리 범위가 불필요하게 넓었습니다.

셋째, session 조회, run별 결과 조회, 상태별 조회, 시간순 로그 조회처럼 서로 다른 접근 패턴을 모두 일반적인 인덱스로 처리하면 데이터 증가 시 조회 비용과 인덱스 관리 비용이 함께 커질 수 있었습니다.

넷째, 운영 DB 데이터를 분석할 때마다 원본 테이블을 직접 JOIN·집계하면 운영 쿼리와 분석 쿼리의 책임이 섞이고 반복 계산 비용이 발생합니다. 따라서 운영 데이터와 분석용 데이터를 분리하고 전체 재처리 대신 변경분만 반영하는 파이프라인이 필요했습니다.

## 1-2. 해결 요구사항

DBA 관점에서는 다음을 요구사항으로 설정했습니다.

* 결과 조회 SQL 수가 데이터 건수에 비례해 증가하지 않아야 한다.
* 실제 조회 패턴을 기준으로 인덱스를 설계한다.
* `EXPLAIN ANALYZE`를 통해 Seq Scan / Index Scan 여부와 실행계획을 확인할 수 있어야 한다.
* 상태 기반 조회에는 전체 인덱스보다 필요한 subset만 인덱싱할 수 있어야 한다.
* 시간순 append 로그는 데이터 특성에 맞는 인덱스를 사용해야 한다.
* 지속적으로 증가하는 로그 데이터는 파티셔닝 가능한 구조로 관리한다.
* 쿼리 시간을 측정하고 일정 기준 이상 느린 쿼리를 확인할 수 있어야 한다.
* 사용하지 않는 DB 객체를 줄여 운영 스키마를 MVP 실행 흐름과 일치시킨다.

DE 관점에서는 다음을 요구사항으로 설정했습니다.

* 운영 DB와 분석용 모델의 책임을 분리한다.
* 분석 데이터는 Fact / Dimension 구조로 제공한다.
* 반복 집계는 매번 원본 테이블에서 계산하지 않는다.
* 전체 적재가 아니라 변경 데이터 중심의 Incremental ETL이 가능해야 한다.
* 변경 이력을 추적할 수 있어야 한다.
* 데이터 적재 후 PK, FK, NULL, accepted value 등의 품질 검사를 수행한다.
* `extract → transform → test → publish` 처리 순서를 명시적인 파이프라인으로 관리한다.
* 데이터 증가에 대응할 수 있는 배치 처리 구조를 준비한다.

---

# 2. 원인 분석

## 2-1. 결과 조회의 N+1 가능성

F-003 결과 API는 하나의 `scenario_result`와 여러 개의 `threshold_result`를 함께 보여줘야 합니다.

기존 구조를 JPA Lazy Loading 방식으로 그대로 구현하면 다음과 같이 동작할 수 있었습니다.

```text
scenario_result 조회 1회
→ threshold_result #1 조회
→ threshold_result #2 조회
→ threshold_result #3 조회
→ ...
```

임계값 결과가 N개라면 SQL 수가 `1 + N`으로 증가할 수 있는 구조였습니다.

이는 단순히 한 번의 쿼리가 느린 문제가 아니라, **데이터가 늘어날수록 DB round trip 자체가 증가하는 구조적 문제**라고 판단했습니다.

---

## 2-2. 실행계획과 조회 패턴 분석

모든 컬럼에 인덱스를 추가하는 방식은 사용하지 않았습니다.

먼저 실제 서비스에서 자주 사용하는 조회 조건을 분리했습니다.

```text
session_uuid
→ 세션 단건 조회

run_id
→ 실행 단위 결과 묶음 조회

scenario_id
→ 시나리오별 결과 조회

session_id + display_order
→ 세션별 시나리오 목록 및 정렬

status = READY
→ 실행 가능한 세션 조회

status = COMPLETED
→ 완료된 run 조회

red_zone = true
→ 위험 임계값 집계

logged_at
→ 시간 범위 계산 로그 조회
```

그리고 `db/scripts/explain_analyze.sql`을 통해 핵심 조회의 실행계획을 확인할 수 있도록 구성했습니다. 판단 기준은 단순한 체감 속도가 아니라 `Seq Scan`, `Index Scan`, 실제 실행 시간 등 DB 실행 경로였습니다.

---

## 2-3. 로그성 데이터의 증가 특성 분석

`calculation_log.logged_at`은 시간이 지날수록 새로운 데이터가 뒤에 append되는 로그 성격을 가집니다.

일반적인 B-tree를 모든 로그 row에 정밀하게 유지하는 것보다, 시간 컬럼과 물리 저장 위치의 상관성이 높은 데이터에서는 BRIN이 더 적합한 후보라고 판단했습니다.

또한 다음 테이블은 시간이 지날수록 계속 증가할 수 있습니다.

```text
pipeline_run_log
simulation_change_log
```

따라서 하나의 거대한 테이블로 계속 유지하는 대신 기간 기준 RANGE Partitioning 대상으로 설계했습니다.

---

## 2-4. 반복 집계 비용 분석

지역별 RIR 요약값을 요청할 때마다 원본 데이터에 대해:

```text
JOIN
→ GROUP BY
→ COUNT / Aggregation
```

을 반복하면 동일한 집계를 매번 다시 계산하게 됩니다.

조회 빈도는 높고 원본 데이터 변경 빈도는 상대적으로 낮은 집계성 결과이므로, 사전 계산된 Materialized View를 제공하는 구조가 적합하다고 판단했습니다.

---

## 2-5. 전체 재처리 방식의 비효율

분석 Fact를 갱신할 때마다 전체 데이터를 다시 처리하면 데이터가 증가할수록 매번 같은 과거 데이터까지 재처리하게 됩니다.

따라서 다음 세 값을 Incremental ETL의 기준으로 사용했습니다.

```text
etl_watermark
updated_at
ON CONFLICT UPSERT
```

마지막 처리 시점 이후 변경된 데이터만 읽어 새 데이터는 INSERT하고 기존 데이터는 UPDATE하는 방식으로 전환했습니다.

---

# 3. 문제 해결 및 적용 과정

## Step 1. N+1 조회를 JOIN 1회로 고정

`ScenarioResultQueryRepository`를 별도로 구성하고 `scenario_result`와 `threshold_result`를 한 번의 JOIN으로 조회하도록 변경했습니다.

### Before

```text
scenario_result 조회
→ threshold_result 추가 조회
→ threshold_result 추가 조회
→ ...
```

### After

```text
scenario_result
       +
threshold_result
       ↓
     JOIN
       ↓
SQL 1회
```

서비스 계층에서는 해당 전용 Repository를 사용하고, 읽기 작업에는 `@Transactional(readOnly = true)`를 적용했습니다.

또한 `spring.jpa.open-in-view=false`를 설정해 Controller/View 단계에서 지연 로딩으로 숨은 SQL이 발생하는 구조를 피했습니다.

마지막으로 `ScenarioResultQueryRepositoryTest`를 추가해 결과 조회가 다시 N+1 방식으로 회귀하지 않도록 검증했습니다.

---

## Step 2. MVP 기준 DB 스키마 슬림화

DB 구조를 기능 가능성 중심이 아니라 실제 MVP 실행 흐름 중심으로 다시 검토했습니다.

Flyway V7에서:

* 미사용 테이블 **11개 제거**
* `scenario_result`의 비-MVP score 컬럼 **8개 제거**

를 수행했습니다.

그 결과 운영 영역은 핵심 시뮬레이션 흐름을 중심으로 단순화하고, 분석 영역은 별도 `analytics` 구조로 분리했습니다.

```text
Operational
- simulation_session
- scenario
- simulation_run
- scenario_result
- threshold_result
- calculation_log
- ...

Analytics
- dim_*
- fact_simulation_run
- materialized view
```

목적은 단순히 테이블 수를 줄이는 것이 아니라 **Entity → Repository → API → Test까지 함께 줄어드는 변경 영향 범위를 명확히 하는 것**이었습니다.

---

## Step 3. 실제 조회 경로 기반 복합 인덱스 설계

MVP에서 자주 사용하는 WHERE / FK / ORDER BY 조건을 기준으로 인덱스를 구성했습니다.

대표적인 조회 패턴은 다음과 같습니다.

```text
session_uuid lookup

run_id → result bundle

scenario_id → result

session_id + display_order
→ session 내부 scenario 목록
```

전체 컬럼에 인덱스를 추가하지 않고 실제 조회 경로 중심으로 선택했습니다.

---

## Step 4. 상태 기반 조회에 Partial Index 적용

전체 row보다 특정 상태만 반복 조회하는 경우에는 Partial Index를 적용했습니다.

대상은 다음과 같습니다.

```text
READY simulation_session
COMPLETED simulation_run
red_zone = true threshold_result
```

즉 전체 데이터를 인덱싱하는 대신, 서비스가 실제 자주 조회하는 subset에만 인덱스를 생성했습니다.

이를 통해 인덱스를 무조건 많이 추가하는 것이 아니라 **조회 빈도와 조건을 기반으로 인덱스 범위를 결정하는 설계**를 적용했습니다.

---

## Step 5. 시계열 로그에 BRIN 적용

`calculation_log.logged_at`은 append 중심의 시간순 로그입니다.

```text
새 로그
→ 시간 증가
→ 뒤쪽 storage에 지속 추가
```

이러한 데이터 특성을 고려해 `logged_at`에 BRIN Index를 적용했습니다.

B-tree와 동일한 방식으로 모든 row에 정밀한 인덱스 entry를 유지하기보다는, 시간 범위 조회에 적합한 block-range 기반 접근을 선택한 것입니다.

---

## Step 6. 증가형 로그 테이블에 RANGE Partitioning 적용

다음 두 로그 테이블을 RANGE Partitioning 대상으로 구성했습니다.

```text
pipeline_run_log
simulation_change_log
```

목적은:

* 기간별 조회 범위 제한
* 오래된 로그 관리 용이성 확보
* 전체 로그 테이블 스캔 부담 감소
* 향후 보관 주기별 파티션 detach/drop 기반 마련

입니다.

---

## Step 7. Materialized View로 반복 집계 분리

지역별 RIR 통계를 매번 원본 테이블에서 계산하는 대신:

```text
analytics.mv_district_rir_summary
```

Materialized View를 구성했습니다.

### Before

```text
API 요청
→ 원본 테이블 JOIN
→ GROUP BY
→ COUNT
→ 결과
```

### After

```text
원본 데이터
→ 사전 집계
→ Materialized View
→ API / Analytics 조회
```

반복 계산 비용을 조회 시점에서 refresh 시점으로 이동했습니다.

---

## Step 8. 운영 DB와 분석 DB 모델 분리

분석을 위해 운영 스키마를 그대로 사용하는 대신 Star Schema를 구성했습니다.

```text
analytics.dim_*
        ↓
fact_simulation_run
```

운영 테이블은 서비스 transaction과 정합성에 최적화하고, Analytics 영역은 날짜·지역·시뮬레이션 실행 단위 집계에 맞도록 별도로 설계했습니다.

이로써:

```text
Operational DB
→ Service/API

Analytics Model
→ DA / Dashboard / Reporting
```

의 책임을 분리했습니다.

---

## Step 9. Incremental ETL + UPSERT 구성

전체 Fact를 매번 다시 적재하지 않고 마지막 처리 이후 변경된 데이터만 갱신하도록 변경했습니다.

```text
etl_watermark
      ↓
updated_at 이후 row
      ↓
Transform
      ↓
ON CONFLICT
  ├─ INSERT
  └─ UPDATE
```

`load.sh --incremental`을 통해 Incremental Load가 가능하도록 구성했습니다.

이 구조의 핵심은 단순 처리속도뿐 아니라 **동일 데이터 재처리 시 중복 생성을 방지하는 idempotent한 적재 방식**에 있습니다.

---

## Step 10. Trigger 기반 CDC-lite 구성

Kafka/Debezium 기반 완전한 CDC를 도입하지 않고 MVP 규모에 맞춰 DB trigger 기반 변경 추적을 구성했습니다.

```text
simulation 데이터 변경
        ↓
PostgreSQL Trigger
        ↓
simulation_change_log
        ↓
Incremental ETL / Audit
```

이를 `CDC-lite`로 명시했습니다.

현재 구현 수준보다 과장해 “실시간 CDC 플랫폼 구축”이라고 표현하지 않고, **DB 변경 이력을 증분 처리에 활용할 수 있는 경량 변경 추적 구조**로 정의했습니다.

---

## Step 11. Data Quality 검사 추가

파이프라인 결과를 단순 적재 성공 여부만으로 판단하지 않고 SQL 기반 품질 검사를 추가했습니다.

검증 대상은:

```text
UNIQUE
NOT NULL
Foreign Key
accepted_values
```

등이며 `run_checks.sql`에서 확인할 수 있도록 구성했습니다.

또한 DE 설계에서는 run 단위로 operational DB와 API response의 reconciliation을 수행하도록 정의했습니다.

```text
run key uniqueness
required input not-null
result-to-run relationship
accepted status
numeric range
request/response schema compatibility
operational DB ↔ API response reconciliation
```

---

## Step 12. Airflow 기반 파이프라인 Orchestration

데이터 작업 순서를 수동 SQL 실행 목록으로 두지 않고 Airflow DAG로 표현했습니다.

```text
extract
   ↓
transform
   ↓
test
   ↓
publish
```

실제 Repository에는:

```text
analytics/airflow/dags/pivot_mvp_pipeline.py
```

가 존재합니다.

파이프라인 단계와 failure boundary를 명시해 데이터 추출·변환·검사·배포를 분리했습니다.

---

## Step 13. Spark 기반 Fact Refresh 확장

데이터 규모 증가에 대비해:

```text
analytics/spark/refresh_fact.py
```

배치를 구성했습니다.

Fact refresh 과정에서 cache와 shuffle partition 조정을 사용할 수 있도록 구성해 단일 SQL 프로세스에만 의존하지 않는 확장 경로를 준비했습니다.

---

## Step 14. DB Query Monitoring 구성

쿼리 개선을 한 번의 튜닝으로 끝내지 않기 위해 Micrometer 기반 `QueryMetricsAspect`를 추가했습니다.

수집 Metric:

```text
pivot.query.duration
```

기준:

```text
Query 실행
→ duration 측정
→ 50ms 이상
→ slow log
→ Prometheus 확인
```

또한 HTTP 요청 시간 측정을 위한 `RequestTimingInterceptor`와 ETL 실행 시간·row count를 기록하는 `PipelineRunLogService`도 구성했습니다.

실행 후 다음 명령으로 metric을 확인할 수 있습니다.

```bash
curl http://localhost:8080/actuator/prometheus | grep pivot
```

---

# 4. 해결 결과 및 성과

## 4-1. N+1 제거

| 측정 지표             |            개선 전 |         개선 후 |                 개선 효과 |
| ----------------- | --------------: | -----------: | --------------------: |
| 임계값 3건 결과 API SQL |              4회 |           1회 |            **75% 감소** |
| 임계값 5건 결과 API SQL |              6회 |           1회 |            **83% 감소** |
| 결과 이력 조회          | `1 + N×M` 증가 가능 | run당 JOIN 1회 | 데이터 증가에 따른 쿼리 수 증가 방지 |

가장 중요한 성과는 **단순 평균 latency가 아니라 결과 개수가 증가해도 SQL 수가 증가하지 않는 조회 구조를 만든 것**입니다.

---

## 4-2. DB 스키마 복잡도 감소

| 지표                         | 개선 전               | 개선 후                       |
| -------------------------- | ------------------ | -------------------------- |
| `scenario_result` score 컬럼 | 9개                 | `housing_score` 중심 1개      |
| 제거한 비-MVP score            | -                  | **8개 제거**                  |
| 운영 테이블                     | ERD v4 기준 약 20개 이상 | **MVP 핵심 10개 + analytics** |
| 제거한 미사용 테이블                | -                  | **11개 제거**                 |

효과는 단순 저장 공간 절감보다 Entity/DTO/API/테스트에서 확인해야 할 범위를 줄인 데 있습니다.

---

## 4-3. 조회 패턴별 DB 구조 개선

| 조회/데이터 특성               | 적용 기술             | 목적                |
| ----------------------- | ----------------- | ----------------- |
| session UUID 단건 조회      | B-tree Index      | 단건 탐색             |
| session + display order | 복합 Index          | 필터 + 정렬           |
| READY 세션                | Partial Index     | subset 조회         |
| COMPLETED run           | Partial Index     | subset 조회         |
| red_zone 결과             | Partial Index     | 위험 데이터 범위 축소      |
| 시간순 calculation log     | BRIN              | 시계열 범위 조회         |
| 계속 증가하는 로그              | RANGE Partition   | 기간 단위 관리          |
| 지역별 RIR 집계              | Materialized View | 반복 aggregation 감소 |

---

## 4-4. 데이터 파이프라인 처리 비용 감소

### Before

```text
운영 DB
→ 매번 전체 데이터 재조회
→ 전체 Transform
→ 전체 Mart 재생성
→ 매번 집계 계산
```

### After

```text
Operational PostgreSQL
       ↓
Change Log / updated_at
       ↓
Watermark
       ↓
Incremental Transform
       ↓
UPSERT
       ↓
Star Schema
       ↓
Materialized View
       ↓
Analytics Serving
```

이 구조를 통해 과거 데이터를 반복 재처리하는 대신 변경분만 반영할 수 있게 했습니다.

현재 README에는 전체 파이프라인의 처리시간 감소율 같은 실측 수치는 없으므로, **“ETL 처리시간을 몇 % 개선했다” 같은 숫자는 사용하지 않습니다.**

---

# 5. DBA 관점 핵심 성과

DBA 포트폴리오에서는 이 프로젝트를 다음 네 가지로 요약할 수 있습니다.

### ① Query Optimization

```text
JPA Lazy N+1
→ 전용 JOIN Repository
→ SQL 수 최대 83% 감소
→ 회귀 테스트 추가
```

### ② Index Design

```text
Actual Query Pattern
→ B-tree / Composite
→ Partial Index
→ BRIN
```

### ③ Storage / Large Table Strategy

```text
Append Log
→ BRIN

Growing Log Tables
→ RANGE Partitioning
```

### ④ Monitoring

```text
Query Duration
→ Micrometer
→ 50ms Slow Log
→ Prometheus
```

---

# 6. DE 관점 핵심 성과

DE 포트폴리오에서는 다음 흐름으로 설명할 수 있습니다.

```text
Operational PostgreSQL
        ↓
CDC-lite / updated_at
        ↓
Incremental ETL
        ↓
Data Quality Test
        ↓
Star Schema
        ↓
Materialized View
        ↓
Analytics Serving
```

여기에 작업 orchestration은:

```text
Airflow
extract
→ transform
→ test
→ publish
```

대용량 배치 확장 경로는:

```text
Spark
→ Fact Refresh
→ Cache
→ Shuffle Partition 조정
```

으로 구성했습니다.

---

# 7. 검증 방법

프로젝트에서 구현한 DB 구조는 다음 순서로 확인할 수 있습니다.

```bash
# PostgreSQL + Backend
docker compose up -d db back

# Flyway V1~V8 + seed + analytics mart
./apps/pivotSeoul/db/load.sh

# EXPLAIN ANALYZE
./apps/pivotSeoul/db/load.sh --explain

# Query / Pipeline Metrics
curl http://localhost:8080/actuator/prometheus | grep pivot
```

검증 축은 다음과 같습니다.

| 검증 대상           | 방법                        |
| --------------- | ------------------------- |
| N+1             | JOIN query count 회귀 테스트   |
| Query Plan      | `EXPLAIN ANALYZE`         |
| Index           | Seq Scan / Index Scan 확인  |
| DQ              | `run_checks.sql`          |
| Mart            | Materialized View refresh |
| Incremental ETL | watermark 이후 데이터 UPSERT   |
| Pipeline        | Airflow DAG 단계 확인         |
| Observability   | Micrometer / Prometheus   |

---

# 8. 회고 및 배운 점

첫째, DB 성능 개선은 단순히 인덱스를 많이 추가하는 작업이 아니라는 점을 배웠습니다.

같은 PostgreSQL에서도 데이터와 조회 특성에 따라:

```text
단건/정렬 조회
→ B-tree

특정 상태 subset
→ Partial Index

시간순 append log
→ BRIN

지속 증가 로그
→ Partitioning
```

처럼 다른 전략이 필요했습니다.

둘째, N+1 문제는 평균 응답시간만으로 발견하기 어려울 수 있다는 점을 확인했습니다. 화면이 정상적으로 동작하더라도 데이터 수에 따라 SQL 호출 횟수가 증가할 수 있기 때문에, 쿼리 수 자체를 회귀 테스트의 검증 지표로 관리했습니다.

셋째, 운영 DB와 분석 DB는 목적이 다르다는 점을 프로젝트 구조에 반영했습니다. OLTP는 서비스의 저장·조회 정합성에 맞추고, 분석은 Fact / Dimension과 사전 집계 결과에 맞게 분리했습니다.

넷째, 데이터 파이프라인의 성능은 Spark 같은 분산처리 기술을 도입하는 것만으로 해결되는 것이 아니라, 먼저 **전체 재처리를 줄이고 변경분만 안전하게 처리하는 Incremental ETL과 idempotency를 설계하는 것이 우선**이라는 점을 배웠습니다.

다섯째, 성능 개선은 일회성 작업이 아니라 운영 중 다시 느려지는 상황을 발견할 수 있어야 의미가 있다고 판단했습니다. 그래서 Query Duration, Slow Log, Pipeline Run Time, Row Count 등의 측정 경로를 함께 구성했습니다.

---

# 9. 현재 프로젝트에서 주장하지 않는 것

이 README는 실제 Repository에서 확인되는 구현을 기준으로 작성했습니다.

따라서 현재 프로젝트에서 확인되지 않은 아래 항목은 성과로 주장하지 않습니다.

* AWS RDS / Aurora 운영
* PgBouncer
* DB CPU 95% → 40%와 같은 CPU 실측
* Connection Pool 고갈 해결
* P99 3초 → 300ms 같은 latency 개선
* Lock / Deadlock 튜닝
* `work_mem` 튜닝
* `CREATE INDEX CONCURRENTLY` 운영 적용
* Backup / Restore 자동화
* HA / Primary-Replica Failover
* RTO / RPO 측정
* Kafka / Debezium 기반 완전한 CDC
* 운영 환경 1,000만 건 이상의 benchmark

해당 항목은 추후 실제 구현·검증 Evidence가 추가된 이후에만 포트폴리오 성과로 추가합니다.

---

# 10. 포트폴리오용 최종 요약

> **pivotSeoul에서 PostgreSQL 기반 시뮬레이션 결과 조회와 분석 데이터 파이프라인을 최적화했습니다. `scenario_result`와 `threshold_result`의 N+1 가능성을 JOIN 1회로 고정해 임계값 5건 기준 SQL을 6회에서 1회로 줄였고, 회귀 테스트를 추가해 쿼리 수 증가를 방지했습니다. 또한 실제 조회 패턴에 맞춰 복합·Partial·BRIN 인덱스를 적용하고, 증가형 로그에는 RANGE Partitioning을 구성했습니다. 운영 데이터와 분석 데이터를 분리하기 위해 Star Schema와 Materialized View를 구성하고, `etl_watermark + updated_at + UPSERT` 기반 증분 ETL과 trigger 기반 CDC-lite를 적용했습니다. 마지막으로 Airflow DAG와 Spark Fact Refresh, SQL Data Quality 검사, Micrometer/Prometheus 기반 Query Monitoring을 구성해 조회 성능뿐 아니라 데이터 처리·검증·운영 관측까지 하나의 흐름으로 연결했습니다.**

## 한 줄 성과

> **결과 조회 SQL을 최대 83% 줄이고, PostgreSQL 인덱스·파티셔닝과 Star Schema·Materialized View·Incremental ETL·Airflow/Spark를 결합해 운영 DB와 분석 파이프라인을 함께 최적화했습니다.**
