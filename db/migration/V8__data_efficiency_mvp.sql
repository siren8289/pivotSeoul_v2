-- =============================================================================
-- MVP 데이터 효율화 (§1~§11, §15 DB 레이어)
-- analytics 스키마: Star Schema · MV · CDC · 파이프라인 로그 · 증분 워터마크
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS analytics;

-- ---------------------------------------------------------------------------
-- §10 증분 처리 워터마크
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS analytics.etl_watermark (
    job_name         VARCHAR(64) PRIMARY KEY,
    last_success_at  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_row_count   BIGINT      NOT NULL DEFAULT 0,
    source_max_ts    TIMESTAMP
);

INSERT INTO analytics.etl_watermark (job_name, last_success_at, last_row_count)
VALUES
    ('reference_load', TIMESTAMP '1970-01-01', 0),
    ('demo_load', TIMESTAMP '1970-01-01', 0),
    ('mart_refresh', TIMESTAMP '1970-01-01', 0)
ON CONFLICT (job_name) DO NOTHING;

-- ---------------------------------------------------------------------------
-- §15 파이프라인 실행 로그 (관측성)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS analytics.pipeline_run_log (
    run_log_id          BIGSERIAL PRIMARY KEY,
    job_name            VARCHAR(64)  NOT NULL,
    started_at          TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at        TIMESTAMP,
    status              VARCHAR(16)  NOT NULL DEFAULT 'RUNNING',
    processed_row_count BIGINT       NOT NULL DEFAULT 0,
    failed_row_count    BIGINT       NOT NULL DEFAULT 0,
    query_runtime_ms    BIGINT,
    source_max_ts       TIMESTAMP,
    target_max_ts       TIMESTAMP,
    error_message       TEXT
) PARTITION BY RANGE (started_at);

CREATE TABLE analytics.pipeline_run_log_2026_q1
    PARTITION OF analytics.pipeline_run_log
    FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');

CREATE TABLE analytics.pipeline_run_log_2026_q2
    PARTITION OF analytics.pipeline_run_log
    FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');

CREATE TABLE analytics.pipeline_run_log_2026_h2
    PARTITION OF analytics.pipeline_run_log
    FOR VALUES FROM ('2026-07-01') TO ('2027-01-01');

CREATE TABLE analytics.pipeline_run_log_default
    PARTITION OF analytics.pipeline_run_log DEFAULT;

CREATE INDEX idx_pipeline_run_log_job_started
    ON analytics.pipeline_run_log (job_name, started_at DESC);

-- ---------------------------------------------------------------------------
-- §11 CDC-lite: 변경 이벤트 로그 (Debezium 대체 MVP 패턴)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS analytics.simulation_change_log (
    change_id    BIGSERIAL PRIMARY KEY,
    table_name   VARCHAR(64)  NOT NULL,
    record_id    BIGINT       NOT NULL,
    operation    VARCHAR(10)  NOT NULL,
    changed_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    payload      JSONB
) PARTITION BY RANGE (changed_at);

CREATE TABLE analytics.simulation_change_log_2026_h1
    PARTITION OF analytics.simulation_change_log
    FOR VALUES FROM ('2026-01-01') TO ('2026-07-01');

CREATE TABLE analytics.simulation_change_log_2026_h2
    PARTITION OF analytics.simulation_change_log
    FOR VALUES FROM ('2026-07-01') TO ('2027-01-01');

CREATE TABLE analytics.simulation_change_log_default
    PARTITION OF analytics.simulation_change_log DEFAULT;

CREATE INDEX idx_simulation_change_log_table_time
    ON analytics.simulation_change_log (table_name, changed_at DESC);

CREATE OR REPLACE FUNCTION analytics.capture_simulation_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_record_id BIGINT;
    v_payload   JSONB;
BEGIN
    v_payload := COALESCE(to_jsonb(NEW), to_jsonb(OLD));
    v_record_id := COALESCE(
        NULLIF(v_payload ->> TG_ARGV[0], '')::BIGINT,
        0
    );

    INSERT INTO analytics.simulation_change_log (table_name, record_id, operation, payload)
    VALUES (TG_TABLE_NAME, v_record_id, TG_OP, v_payload);

    RETURN COALESCE(NEW, OLD);
END;
$$;

DROP TRIGGER IF EXISTS trg_simulation_session_cdc ON simulation_session;
CREATE TRIGGER trg_simulation_session_cdc
    AFTER INSERT OR UPDATE OR DELETE ON simulation_session
    FOR EACH ROW EXECUTE FUNCTION analytics.capture_simulation_change('session_id');

DROP TRIGGER IF EXISTS trg_simulation_run_cdc ON simulation_run;
CREATE TRIGGER trg_simulation_run_cdc
    AFTER INSERT OR UPDATE OR DELETE ON simulation_run
    FOR EACH ROW EXECUTE FUNCTION analytics.capture_simulation_change('simulation_run_id');

DROP TRIGGER IF EXISTS trg_scenario_result_cdc ON scenario_result;
CREATE TRIGGER trg_scenario_result_cdc
    AFTER INSERT OR UPDATE OR DELETE ON scenario_result
    FOR EACH ROW EXECUTE FUNCTION analytics.capture_simulation_change('scenario_result_id');

-- ---------------------------------------------------------------------------
-- §1·§2 Star Schema (분석 마트)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_id    INTEGER PRIMARY KEY,
    full_date  DATE    NOT NULL UNIQUE,
    year       INTEGER NOT NULL,
    quarter    INTEGER NOT NULL,
    month      INTEGER NOT NULL,
    day        INTEGER NOT NULL
);

INSERT INTO analytics.dim_date (date_id, full_date, year, quarter, month, day)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER,
    d::DATE,
    EXTRACT(YEAR FROM d)::INTEGER,
    EXTRACT(QUARTER FROM d)::INTEGER,
    EXTRACT(MONTH FROM d)::INTEGER,
    EXTRACT(DAY FROM d)::INTEGER
FROM generate_series(DATE '2024-01-01', DATE '2027-12-31', INTERVAL '1 day') AS d
ON CONFLICT (date_id) DO NOTHING;

CREATE OR REPLACE VIEW analytics.dim_life_stage AS
SELECT life_stage_id, stage_code, stage_name, description
FROM life_stage;

CREATE OR REPLACE VIEW analytics.dim_district AS
SELECT district_id, district_code, district_name, region_group
FROM district;

CREATE TABLE IF NOT EXISTS analytics.fact_simulation_run (
    fact_id             BIGSERIAL PRIMARY KEY,
    simulation_run_id   BIGINT         NOT NULL UNIQUE,
    session_id          BIGINT         NOT NULL,
    scenario_result_id  BIGINT,
    life_stage_id       BIGINT,
    life_stage_code     VARCHAR(32),
    current_district    VARCHAR(64),
    run_date_id         INTEGER REFERENCES analytics.dim_date (date_id),
    rir_value           NUMERIC(14, 6),
    is_red_zone         BOOLEAN        NOT NULL DEFAULT FALSE,
    risk_score          NUMERIC(14, 6),
    run_status          VARCHAR(32),
    refreshed_at        TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fact_simulation_run_date ON analytics.fact_simulation_run (run_date_id);
CREATE INDEX idx_fact_simulation_run_district ON analytics.fact_simulation_run (current_district);
CREATE INDEX idx_fact_simulation_run_red_zone ON analytics.fact_simulation_run (is_red_zone);

-- ---------------------------------------------------------------------------
-- §9 Materialized View — 자치구별 RIR 요약
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_district_rir_summary AS
SELECT
    f.current_district,
    COUNT(*)                                                   AS run_count,
    ROUND(AVG(f.rir_value), 4)                                 AS avg_rir,
    SUM(CASE WHEN f.is_red_zone THEN 1 ELSE 0 END)               AS red_zone_count,
    MAX(f.refreshed_at)                                        AS last_refreshed_at
FROM analytics.fact_simulation_run f
WHERE f.current_district IS NOT NULL
GROUP BY f.current_district
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_district_rir_summary_district
    ON analytics.mv_district_rir_summary (current_district);

-- ---------------------------------------------------------------------------
-- §10 증분 컬럼 (운영 테이블)
-- ---------------------------------------------------------------------------
ALTER TABLE simulation_session
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE simulation_run
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE calculation_log
    ADD COLUMN IF NOT EXISTS logged_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- ---------------------------------------------------------------------------
-- §5·§6 Partial / Composite Index
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_simulation_session_uuid
    ON simulation_session (session_uuid);

CREATE INDEX IF NOT EXISTS idx_simulation_session_ready_created
    ON simulation_session (created_at DESC)
    WHERE session_status = 'READY';

CREATE INDEX IF NOT EXISTS idx_simulation_run_completed
    ON simulation_run (session_id, completed_at DESC)
    WHERE run_status = 'COMPLETED';

CREATE INDEX IF NOT EXISTS idx_threshold_result_red_zone
    ON threshold_result (scenario_result_id, calculated_value)
    WHERE is_red_zone = TRUE;

CREATE INDEX IF NOT EXISTS idx_threshold_result_housing_lookup
    ON threshold_result (scenario_result_id, threshold_type_id);

-- ---------------------------------------------------------------------------
-- §7·§8 calculation_log — BRIN(시계열) + logged_at 파티션 프루닝 보조
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_calculation_log_logged_at_brin
    ON calculation_log USING BRIN (logged_at);
