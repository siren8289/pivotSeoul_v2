# DB (`db/`)

스키마·데모 적재를 **최상위 `db/` 폴더**에서 관리합니다.

```
db/
  migration/     # Flyway V1~V8 → 빌드 시 classpath:db/migration
  data/          # 개발·QA 데모 SQL
  load.sh        # data 적재
  reset-demo.sh  # demo-*만 삭제
```

| 하위 | 역할 |
|------|------|
| `migration/` | Flyway V1~V8 (스키마 + 데이터 효율화) |
| `data/` | 마스터·자치구·데모·**마트 갱신** |
| `quality/` | DBQC SQL (`run_checks.sql`) |
| `scripts/` | `EXPLAIN ANALYZE` (`explain_analyze.sql`) |

백엔드 기동 시 Gradle이 `db/migration/`을 `classpath:db/migration`으로 패키징하고, Flyway가 적용합니다.

## 사용법

```bash
docker compose up -d db back   # Flyway migrate
./db/load.sh                   # 데모 + 마트 + 품질
./db/load.sh --incremental
./db/load.sh --explain         # EXPLAIN ANALYZE
./db/reset-demo.sh && ./db/load.sh --demo-only
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
