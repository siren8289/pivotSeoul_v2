-- §2·§9·§10 분석 마트 증분 갱신 + Materialized View REFRESH
-- updated_at 워터마크 이후 변경분만 fact에 upsert

\set ON_ERROR_STOP on

DO $$
DECLARE
    v_watermark   TIMESTAMP;
    v_processed   BIGINT := 0;
    v_run_log_id  BIGINT;
BEGIN
    SELECT COALESCE(source_max_ts, TIMESTAMP '1970-01-01')
    INTO v_watermark
    FROM analytics.etl_watermark
    WHERE job_name = 'mart_refresh';

    INSERT INTO analytics.pipeline_run_log (job_name, status)
    VALUES ('mart_refresh', 'RUNNING')
    RETURNING run_log_id INTO v_run_log_id;

    INSERT INTO analytics.fact_simulation_run (
        simulation_run_id,
        session_id,
        scenario_result_id,
        life_stage_id,
        life_stage_code,
        current_district,
        run_date_id,
        rir_value,
        is_red_zone,
        risk_score,
        run_status,
        refreshed_at
    )
    SELECT
        r.simulation_run_id,
        r.session_id,
        sr.scenario_result_id,
        s.life_stage_id,
        ls.stage_code,
        uc.current_district,
        TO_CHAR(COALESCE(r.completed_at, r.started_at, NOW()), 'YYYYMMDD')::INTEGER,
        tr.calculated_value,
        COALESCE(tr.is_red_zone, FALSE),
        sr.risk_score,
        r.run_status,
        NOW()
    FROM simulation_run r
    JOIN simulation_session s ON s.session_id = r.session_id
    JOIN life_stage ls ON ls.life_stage_id = s.life_stage_id
    LEFT JOIN user_condition uc ON uc.session_id = s.session_id
    LEFT JOIN scenario_result sr ON sr.simulation_run_id = r.simulation_run_id
    LEFT JOIN threshold_result tr ON tr.scenario_result_id = sr.scenario_result_id
    WHERE r.run_status = 'COMPLETED'
      AND GREATEST(
            COALESCE(r.updated_at, r.completed_at, r.started_at),
            COALESCE(s.updated_at, s.created_at)
          ) > v_watermark
    ON CONFLICT (simulation_run_id) DO UPDATE SET
        session_id = EXCLUDED.session_id,
        scenario_result_id = EXCLUDED.scenario_result_id,
        life_stage_id = EXCLUDED.life_stage_id,
        life_stage_code = EXCLUDED.life_stage_code,
        current_district = EXCLUDED.current_district,
        run_date_id = EXCLUDED.run_date_id,
        rir_value = EXCLUDED.rir_value,
        is_red_zone = EXCLUDED.is_red_zone,
        risk_score = EXCLUDED.risk_score,
        run_status = EXCLUDED.run_status,
        refreshed_at = NOW();

    GET DIAGNOSTICS v_processed = ROW_COUNT;

    REFRESH MATERIALIZED VIEW analytics.mv_district_rir_summary;

    UPDATE analytics.etl_watermark
    SET last_success_at = NOW(),
        last_row_count = v_processed,
        source_max_ts = (
            SELECT MAX(GREATEST(
                COALESCE(r.updated_at, r.completed_at, r.started_at),
                COALESCE(s.updated_at, s.created_at)
            ))
            FROM simulation_run r
            JOIN simulation_session s ON s.session_id = r.session_id
        )
    WHERE job_name = 'mart_refresh';

    UPDATE analytics.pipeline_run_log
    SET status = 'SUCCESS',
        completed_at = NOW(),
        processed_row_count = v_processed,
        target_max_ts = NOW()
    WHERE run_log_id = v_run_log_id;
END $$;

SELECT current_district, run_count, avg_rir, red_zone_count
FROM analytics.mv_district_rir_summary
ORDER BY run_count DESC
LIMIT 10;
