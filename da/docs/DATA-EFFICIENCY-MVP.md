# Pivot Seoul MVP — 데이터 효율화 적용 현황

> 공식 문서 기반 17단계 중 **이 프로젝트에 실제 구현·반영된 항목만** 정리.

---

## 적용 요약

| § | 항목 | 상태 | 구현 위치 |
|---|------|------|-----------|
| 0 | 지표 측정 | ✅ | Micrometer `pivot.query.duration`, `pivot.http.server.requests`, Actuator `/actuator/prometheus` |
| 1 | 데이터 모델 정리 | ✅ | V7 미사용 테이블·wide 컬럼 제거 |
| 2 | Star Schema | ✅ | V8 `analytics.dim_*`, `analytics.fact_simulation_run` |
| 3 | 실행계획 확인 | ✅ | `back/db/scripts/explain_analyze.sql`, `load.sh --explain` |
| 4 | SQL 최적화 | ✅ | `ScenarioResultQueryRepository` JOIN 1회 (N+1 제거) |
| 5 | 인덱스 | ✅ | V7 + V8 복합 인덱스 |
| 6 | Partial Index | ✅ | V8 `idx_simulation_run_completed`, `idx_threshold_result_red_zone` 등 |
| 7 | 파티셔닝 | ✅ | V8 `pipeline_run_log`, `simulation_change_log` RANGE 파티션 |
| 8 | 클러스터링 | ✅ | V8 `calculation_log` BRIN(`logged_at`) — PG 시계열 군집 |
| 9 | Materialized View | ✅ | V8 `analytics.mv_district_rir_summary` + `da/sql/06_refresh_analytics_mart.sql` |
| 10 | 증분 처리 | ✅ | `updated_at` 컬럼, `etl_watermark`, mart UPSERT, `load.sh --incremental` |
| 11 | CDC | ✅ | V8 trigger → `analytics.simulation_change_log` (Debezium-lite) |
| 12 | Spark 튜닝 | ✅ | `da/spark/refresh_fact.py` (cache, shuffle partitions, Kryo) |
| 13 | 품질 테스트 | ✅ | `back/db/quality/run_checks.sql` (unique/not_null/FK/accepted_values) |
| 14 | Airflow | ✅ | `da/airflow/dags/pivot_mvp_pipeline.py` |
| 15 | 관측성 | ✅ | `analytics.pipeline_run_log`, `PipelineRunLogService`, Actuator metrics |

---

## 포트폴리오 문장

```
운영 DB는 MVP 범위에 맞게 정규화·슬림화(V7)하고, 조회 경로별 인덱스·Partial Index·BRIN을 설계(V8)했다.
F-003 결과 API는 scenario_result + threshold_result JOIN 1회로 N+1을 제거했고,
EXPLAIN ANALYZE 스크립트로 실행계획을 검증할 수 있게 했다.

분석 영역은 analytics 스키마에 Star Schema(fact/dim)와 Materialized View를 두고,
updated_at 워터마크 기반 증분 mart 갱신, CDC-lite 변경 로그, Airflow DAG, Spark 배치 스크립트로
파이프라인 효율화를 구성했다. 품질은 SQL 기반 DBQC, 운영은 Micrometer·pipeline_run_log로 추적한다.
```

---

## 실행 방법

```bash
# Flyway V1~V8 (docker compose up 시 자동)
docker compose up -d db back

# 마스터 + 데모 + 마트 + 품질
./back/db/load.sh

# 증분만
./back/db/load.sh --incremental

# 실행계획
./back/db/load.sh --explain

# 메트릭
curl http://localhost:8080/actuator/prometheus | grep pivot
```

---

## 미적용 / 향후

| 항목 | 이유 |
|------|------|
| Debezium/Kafka full CDC | MVP 규모 — DB trigger 기반 lite CDC로 대체 |
| BigQuery clustering | PostgreSQL 운영 — BRIN으로 대체 |
| dbt Cloud | SQL 품질 스크립트로 대체, 추후 dbt 이관 가능 |
| OpenTelemetry Collector | Micrometer + pipeline_run_log로 1차 대체 |

---

## 변경 파일

### DB
- `back/db/migration/V8__data_efficiency_mvp.sql`
- `da/sql/06_refresh_analytics_mart.sql`
- `back/db/quality/run_checks.sql`
- `back/db/scripts/explain_analyze.sql`
- `back/db/load.sh`

### Backend
- `ScenarioResultQueryRepository`, `ScenarioResultBundle`
- `SimulationResultService` (JOIN 조회)
- `PipelineRunLogService`, `QueryMetricsAspect`, `RequestTimingInterceptor`
- `build.gradle` (actuator, aop)
- `application.yml` (prometheus)

### Analytics
- `da/airflow/dags/pivot_mvp_pipeline.py`
- `da/spark/refresh_fact.py`
