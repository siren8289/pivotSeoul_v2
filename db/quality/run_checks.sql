-- §13 데이터 품질 테스트 (dbt generic test 대응 MVP SQL)
-- 실패 시 non-zero exit: ON_ERROR_STOP

\set ON_ERROR_STOP on

\echo 'DBQC-001 life_stage unique + not_null'
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM life_stage) <> 3 THEN
        RAISE EXCEPTION 'DBQC-001 failed: expected 3 life_stage rows';
    END IF;
    IF EXISTS (SELECT stage_code FROM life_stage GROUP BY stage_code HAVING COUNT(*) > 1) THEN
        RAISE EXCEPTION 'DBQC-001 failed: duplicate stage_code';
    END IF;
    IF EXISTS (SELECT 1 FROM life_stage WHERE stage_code IS NULL OR stage_name IS NULL) THEN
        RAISE EXCEPTION 'DBQC-001 failed: null in life_stage';
    END IF;
END $$;

\echo 'DBQC-002 threshold_type HOUSING'
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM threshold_type WHERE threshold_code = 'HOUSING') <> 1 THEN
        RAISE EXCEPTION 'DBQC-002 failed: HOUSING threshold missing';
    END IF;
END $$;

\echo 'DBQC-003 FK user_condition -> simulation_session'
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM user_condition uc
        LEFT JOIN simulation_session s ON s.session_id = uc.session_id
        WHERE s.session_id IS NULL
    ) THEN
        RAISE EXCEPTION 'DBQC-003 failed: orphan user_condition';
    END IF;
END $$;

\echo 'DBQC-004 scenario_result FK integrity'
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM scenario_result sr
        LEFT JOIN simulation_run r ON r.simulation_run_id = sr.simulation_run_id
        WHERE r.simulation_run_id IS NULL
    ) THEN
        RAISE EXCEPTION 'DBQC-004 failed: orphan scenario_result';
    END IF;
END $$;

\echo 'DBQC-005 threshold_result accepted_values + red_zone consistency'
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM threshold_result
        WHERE threshold_status NOT IN ('STABLE', 'WARNING', 'DANGER', 'UNKNOWN')
           OR calculated_value < 0
    ) THEN
        RAISE EXCEPTION 'DBQC-005 failed: invalid threshold_result values';
    END IF;
    IF EXISTS (
        SELECT 1
        FROM threshold_result
        WHERE is_red_zone = TRUE AND calculated_value <= 0.4
    ) THEN
        RAISE EXCEPTION 'DBQC-005 failed: red_zone without RIR > 0.4';
    END IF;
END $$;

\echo 'DBQC-006 demo sessions row count guard'
DO $$
DECLARE
    demo_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO demo_count FROM simulation_session WHERE session_uuid LIKE 'demo-%';
    IF demo_count > 0 AND demo_count <> 4 THEN
        RAISE EXCEPTION 'DBQC-006 failed: expected 0 or 4 demo sessions, got %', demo_count;
    END IF;
END $$;

\echo 'DBQC-007 analytics fact not stale vs operational (if mart loaded)'
DO $$
DECLARE
    op_count BIGINT;
    fact_count BIGINT;
BEGIN
    SELECT COUNT(*) INTO op_count
    FROM simulation_run
    WHERE run_status = 'COMPLETED';

    SELECT COUNT(*) INTO fact_count FROM analytics.fact_simulation_run;

    IF op_count > 0 AND fact_count = 0 THEN
        RAISE WARNING 'DBQC-007 warn: completed runs exist but fact table empty — run 06_refresh_analytics_mart.sql';
    END IF;
END $$;

\echo 'All quality checks passed.'
