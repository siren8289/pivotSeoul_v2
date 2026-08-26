# DB (`back/db/`)

스키마·데모 적재는 `back/db/`, DA 산출물은 `da/`에서 관리합니다.

```
back/db/
  migration/     # Flyway V1~V8 → 빌드 시 classpath:db/migration
  data/          # 개발·QA 데모 SQL
  load.sh        # data 적재
  reset-demo.sh  # demo-*만 삭제

da/
  docs/          # 데이터 효율화/분석 문서
  airflow/dags/  # Airflow DAG
  spark/         # Spark 배치
  sql/           # 분석 마트 갱신 SQL
```

| 하위 | 역할 |
|------|------|
| `migration/` | Flyway V1~V8 (스키마 + 데이터 효율화) |
| `data/` | 마스터·자치구·데모 SQL |
| `quality/` | DBQC SQL (`run_checks.sql`) |
| `scripts/` | `EXPLAIN ANALYZE` (`explain_analyze.sql`) |
| `../../da/` | DA 문서·파이프라인·SQL 산출물 |

## 사용법

```bash
docker compose up -d db back   # Flyway migrate
./back/db/load.sh              # 데모 + 마트 + 품질
./back/db/load.sh --incremental
./back/db/load.sh --explain    # EXPLAIN ANALYZE
./back/db/reset-demo.sh && ./back/db/load.sh --demo-only
```

## 데모 세션

| session_uuid | 용도 |
|--------------|------|
| `demo-ready-001` | Run API 수동 테스트 |
| `demo-stable-001` | RIR 0.30 |
| `demo-warning-001` | RIR 0.40 |
| `demo-redzone-001` | RIR 0.45 Red Zone |

```sql
SELECT s.session_uuid, sr.scenario_result_id
FROM simulation_session s
LEFT JOIN scenario_result sr ON sr.simulation_run_id IN (
  SELECT simulation_run_id FROM simulation_run WHERE session_id = s.session_id
)
WHERE s.session_uuid LIKE 'demo-%';
```
