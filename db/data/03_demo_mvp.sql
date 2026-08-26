-- TEST-QAQC TD-001~004 대응 데모 데이터 (Flyway 스키마 적용 후 실행)
-- 재실행 시 demo-* 세션부터 제거 후 다시 적재

DELETE FROM simulation_session WHERE session_uuid LIKE 'demo-%';

DO $$
DECLARE
    v_youth_id          BIGINT;
    v_housing_type_id   BIGINT;
    v_session_id        BIGINT;
    v_scenario_id       BIGINT;
    v_run_id            BIGINT;
    v_result_id         BIGINT;
    v_risk              NUMERIC;
    v_total             NUMERIC;
BEGIN
    SELECT life_stage_id INTO v_youth_id FROM life_stage WHERE stage_code = 'YOUTH';
    SELECT threshold_type_id INTO v_housing_type_id FROM threshold_type WHERE threshold_code = 'HOUSING';

    IF v_youth_id IS NULL OR v_housing_type_id IS NULL THEN
        RAISE EXCEPTION 'Run 01_reference.sql first (life_stage, threshold_type)';
    END IF;

    -- -------------------------------------------------------------------------
    -- demo-ready-001: 세션만 (F-002 Run API 수동 테스트 — TD-001)
    -- -------------------------------------------------------------------------
    INSERT INTO simulation_session (session_uuid, life_stage_id, session_status, consent_to_save_result, created_at)
    VALUES ('demo-ready-001', v_youth_id, 'READY', false, NOW())
    RETURNING session_id INTO v_session_id;

    INSERT INTO user_condition (session_id, current_district, monthly_income, monthly_housing)
    VALUES (v_session_id, '마포구', 4500000, 1800000);

    INSERT INTO scenario (session_id, scenario_type, scenario_title, display_order)
    VALUES (v_session_id, 'A', '데모 — Run 대기 (TD-001)', 1);

    -- -------------------------------------------------------------------------
    -- demo-stable-001: RIR 0.30 (TD-004)
    -- -------------------------------------------------------------------------
    INSERT INTO simulation_session (session_uuid, life_stage_id, session_status, consent_to_save_result, created_at)
    VALUES ('demo-stable-001', v_youth_id, 'READY', true, NOW())
    RETURNING session_id INTO v_session_id;

    INSERT INTO user_condition (session_id, current_district, monthly_income, monthly_housing)
    VALUES (v_session_id, '마포구', 5000000, 1500000);

    INSERT INTO scenario (session_id, scenario_type, scenario_title, display_order)
    VALUES (v_session_id, 'A', '데모 — stable RIR 0.30', 1)
    RETURNING scenario_id INTO v_scenario_id;

    INSERT INTO simulation_run (
        session_id, run_status, calculation_engine_version, ai_pipeline_version,
        model_version, total_confidence_score, started_at, completed_at
    ) VALUES (
        v_session_id, 'COMPLETED', 'MVP_V1', 'FASTAPI_HOUSING_V1', 'RIR_RULE_V1',
        0.85, NOW() - INTERVAL '2 minutes', NOW() - INTERVAL '1 minute'
    ) RETURNING simulation_run_id INTO v_run_id;

    v_risk := 20;
    v_total := 100 - v_risk;

    INSERT INTO scenario_result (
        simulation_run_id, scenario_id, result_status, total_score, risk_score,
        confidence_score, housing_score
    ) VALUES (
        v_run_id, v_scenario_id, 'STABLE', v_total, v_risk, 0.85, v_risk
    ) RETURNING scenario_result_id INTO v_result_id;

    INSERT INTO threshold_result (
        scenario_result_id, threshold_type_id, threshold_status,
        calculated_value, threshold_value, is_red_zone, calculation_summary
    ) VALUES (
        v_result_id, v_housing_type_id, 'STABLE',
        0.30, 0.4, false, 'RIR=0.30, status=STABLE, redZone=false (demo load)'
    );

    -- -------------------------------------------------------------------------
    -- demo-warning-001: RIR 0.40 경계 (TD-003)
    -- -------------------------------------------------------------------------
    INSERT INTO simulation_session (session_uuid, life_stage_id, session_status, consent_to_save_result, created_at)
    VALUES ('demo-warning-001', v_youth_id, 'READY', true, NOW())
    RETURNING session_id INTO v_session_id;

    INSERT INTO user_condition (session_id, current_district, monthly_income, monthly_housing)
    VALUES (v_session_id, '마포구', 5000000, 2000000);

    INSERT INTO scenario (session_id, scenario_type, scenario_title, display_order)
    VALUES (v_session_id, 'A', '데모 — warning RIR 0.40', 1)
    RETURNING scenario_id INTO v_scenario_id;

    INSERT INTO simulation_run (
        session_id, run_status, calculation_engine_version, ai_pipeline_version,
        model_version, total_confidence_score, started_at, completed_at
    ) VALUES (
        v_session_id, 'COMPLETED', 'MVP_V1', 'FASTAPI_HOUSING_V1', 'RIR_RULE_V1',
        0.85, NOW() - INTERVAL '2 minutes', NOW() - INTERVAL '1 minute'
    ) RETURNING simulation_run_id INTO v_run_id;

    v_risk := 50;
    v_total := 100 - v_risk;

    INSERT INTO scenario_result (
        simulation_run_id, scenario_id, result_status, total_score, risk_score,
        confidence_score, housing_score
    ) VALUES (
        v_run_id, v_scenario_id, 'WARNING', v_total, v_risk, 0.85, v_risk
    ) RETURNING scenario_result_id INTO v_result_id;

    INSERT INTO threshold_result (
        scenario_result_id, threshold_type_id, threshold_status,
        calculated_value, threshold_value, is_red_zone, calculation_summary
    ) VALUES (
        v_result_id, v_housing_type_id, 'WARNING',
        0.40, 0.4, false, 'RIR=0.40, status=WARNING, redZone=false (demo load)'
    );

    -- -------------------------------------------------------------------------
    -- demo-redzone-001: RIR 0.45 Red Zone (TD-002, TC-009)
    -- -------------------------------------------------------------------------
    INSERT INTO simulation_session (session_uuid, life_stage_id, session_status, consent_to_save_result, created_at)
    VALUES ('demo-redzone-001', v_youth_id, 'READY', true, NOW())
    RETURNING session_id INTO v_session_id;

    INSERT INTO user_condition (session_id, current_district, monthly_income, monthly_housing)
    VALUES (v_session_id, '마포구', 5000000, 2250000);

    INSERT INTO scenario (session_id, scenario_type, scenario_title, display_order)
    VALUES (v_session_id, 'A', '데모 — Red Zone RIR 0.45', 1)
    RETURNING scenario_id INTO v_scenario_id;

    INSERT INTO simulation_run (
        session_id, run_status, calculation_engine_version, ai_pipeline_version,
        model_version, total_confidence_score, started_at, completed_at
    ) VALUES (
        v_session_id, 'COMPLETED', 'MVP_V1', 'FASTAPI_HOUSING_V1', 'RIR_RULE_V1',
        0.85, NOW() - INTERVAL '2 minutes', NOW() - INTERVAL '1 minute'
    ) RETURNING simulation_run_id INTO v_run_id;

    v_risk := 80;
    v_total := 100 - v_risk;

    INSERT INTO scenario_result (
        simulation_run_id, scenario_id, result_status, total_score, risk_score,
        confidence_score, housing_score
    ) VALUES (
        v_run_id, v_scenario_id, 'DANGER', v_total, v_risk, 0.85, v_risk
    ) RETURNING scenario_result_id INTO v_result_id;

    INSERT INTO threshold_result (
        scenario_result_id, threshold_type_id, threshold_status,
        calculated_value, threshold_value, is_red_zone, calculation_summary
    ) VALUES (
        v_result_id, v_housing_type_id, 'DANGER',
        0.45, 0.4, true, 'RIR=0.45, status=DANGER, redZone=true (demo load)'
    );
END $$;

-- 적재 확인
SELECT s.session_uuid,
       s.session_id,
       sr.scenario_result_id,
       tr.calculated_value AS rir,
       tr.is_red_zone
FROM simulation_session s
LEFT JOIN simulation_run r ON r.session_id = s.session_id
LEFT JOIN scenario_result sr ON sr.simulation_run_id = r.simulation_run_id
LEFT JOIN threshold_result tr ON tr.scenario_result_id = sr.scenario_result_id
WHERE s.session_uuid LIKE 'demo-%'
ORDER BY s.session_uuid;
