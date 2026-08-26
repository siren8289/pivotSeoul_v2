-- =============================================================================
-- MVP — 미사용 테이블·컬럼 제거 (ERD v4 비-MVP 잔재)
-- 유지: life_stage, district, simulation_session, user_condition, scenario,
--       simulation_run, scenario_result, threshold_type, threshold_result,
--       calculation_log
-- =============================================================================

DROP TABLE IF EXISTS threshold_data_provenance CASCADE;
DROP TABLE IF EXISTS simulation_data_usage CASCADE;
DROP TABLE IF EXISTS dataset_validation_result CASCADE;
DROP TABLE IF EXISTS data_snapshot CASCADE;
DROP TABLE IF EXISTS data_source CASCADE;
DROP TABLE IF EXISTS dataset_registry CASCADE;
DROP TABLE IF EXISTS weekly_action CASCADE;
DROP TABLE IF EXISTS recovery_lever CASCADE;
DROP TABLE IF EXISTS red_zone_rule CASCADE;
DROP TABLE IF EXISTS external_service_link CASCADE;
DROP TABLE IF EXISTS scenario_comparison CASCADE;
DROP TABLE IF EXISTS scenario_input_summary CASCADE;

-- MVP 미사용 도메인 점수 컬럼 (housing_score만 사용)
ALTER TABLE scenario_result DROP COLUMN IF EXISTS disposable_income_score;
ALTER TABLE scenario_result DROP COLUMN IF EXISTS career_score;
ALTER TABLE scenario_result DROP COLUMN IF EXISTS time_loss_score;
ALTER TABLE scenario_result DROP COLUMN IF EXISTS opportunity_index;
ALTER TABLE scenario_result DROP COLUMN IF EXISTS childcare_score;
ALTER TABLE scenario_result DROP COLUMN IF EXISTS policy_score;
ALTER TABLE scenario_result DROP COLUMN IF EXISTS senior_sustainability_score;

-- F-002 scenario 조회용 (§5)
CREATE INDEX IF NOT EXISTS idx_scenario_session_id
ON scenario (session_id, display_order, scenario_id);
