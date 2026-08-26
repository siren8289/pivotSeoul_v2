-- =============================================================================
-- ERD v4 — 임계점·회복 레버·데이터 계보 (§2 주거 / §7 데이터 출처 / §8 계산 감사)
-- docs/erd-v4/02-housing.md, 07-data-provenance.md, 08-llm-audit.md 정렬
-- =============================================================================

-- §1 확장: 기능별 점수·입력 요약·run 메타
ALTER TABLE scenario_result ADD COLUMN IF NOT EXISTS housing_score NUMERIC(14, 6);
ALTER TABLE scenario_result ADD COLUMN IF NOT EXISTS disposable_income_score NUMERIC(14, 6);
ALTER TABLE scenario_result ADD COLUMN IF NOT EXISTS career_score NUMERIC(14, 6);
ALTER TABLE scenario_result ADD COLUMN IF NOT EXISTS time_loss_score NUMERIC(14, 6);
ALTER TABLE scenario_result ADD COLUMN IF NOT EXISTS opportunity_index NUMERIC(14, 6);
ALTER TABLE scenario_result ADD COLUMN IF NOT EXISTS childcare_score NUMERIC(14, 6);
ALTER TABLE scenario_result ADD COLUMN IF NOT EXISTS policy_score NUMERIC(14, 6);
ALTER TABLE scenario_result ADD COLUMN IF NOT EXISTS senior_sustainability_score NUMERIC(14, 6);

ALTER TABLE scenario_input_summary ADD COLUMN IF NOT EXISTS skill_level VARCHAR(64);
ALTER TABLE scenario_input_summary ADD COLUMN IF NOT EXISTS weekly_learning_hours INTEGER;
ALTER TABLE scenario_input_summary ADD COLUMN IF NOT EXISTS commute_time_band VARCHAR(64);
ALTER TABLE scenario_input_summary ADD COLUMN IF NOT EXISTS health_status_group VARCHAR(64);

ALTER TABLE simulation_run ADD COLUMN IF NOT EXISTS model_version VARCHAR(128);

-- V2 스텁 제거 후 본 스키마로 재생성
DROP TABLE IF EXISTS calculation_log CASCADE;
DROP TABLE IF EXISTS weekly_action CASCADE;
DROP TABLE IF EXISTS recovery_lever CASCADE;
DROP TABLE IF EXISTS red_zone_rule CASCADE;
DROP TABLE IF EXISTS threshold_result CASCADE;

CREATE TABLE threshold_type (
    threshold_type_id BIGSERIAL PRIMARY KEY,
    threshold_code    VARCHAR(64)  NOT NULL UNIQUE,
    threshold_name    VARCHAR(256) NOT NULL,
    formula_version   TEXT,
    unit_default      VARCHAR(64)
);

CREATE TABLE external_service_link (
    service_link_id BIGSERIAL PRIMARY KEY,
    link_type       VARCHAR(64),
    title           VARCHAR(512),
    url             VARCHAR(2048) NOT NULL,
    provider        VARCHAR(128)
);

CREATE TABLE threshold_result (
    threshold_result_id BIGSERIAL PRIMARY KEY,
    scenario_result_id  BIGINT       NOT NULL REFERENCES scenario_result (scenario_result_id) ON DELETE CASCADE,
    threshold_type_id   BIGINT       NOT NULL REFERENCES threshold_type (threshold_type_id),
    threshold_status    VARCHAR(32),
    calculated_value    NUMERIC(14, 6),
    threshold_value     NUMERIC(14, 6),
    is_red_zone         BOOLEAN      NOT NULL DEFAULT FALSE,
    calculation_summary TEXT
);

CREATE INDEX idx_threshold_result_scenario ON threshold_result (scenario_result_id);
CREATE INDEX idx_threshold_result_type ON threshold_result (threshold_type_id);

CREATE TABLE red_zone_rule (
    red_zone_rule_id  BIGSERIAL PRIMARY KEY,
    threshold_type_id BIGINT       NOT NULL REFERENCES threshold_type (threshold_type_id) ON DELETE CASCADE,
    rule_code         VARCHAR(64)  NOT NULL,
    trigger_value     NUMERIC(14, 6),
    trigger_operator  VARCHAR(16),
    rule_description  TEXT
);

CREATE TABLE recovery_lever (
    recovery_lever_id    BIGSERIAL PRIMARY KEY,
    threshold_result_id  BIGINT NOT NULL REFERENCES threshold_result (threshold_result_id) ON DELETE CASCADE,
    lever_type           VARCHAR(64),
    lever_title          VARCHAR(512),
    lever_description    TEXT,
    expected_effect_score NUMERIC(14, 6),
    service_link_id      BIGINT REFERENCES external_service_link (service_link_id)
);

CREATE TABLE weekly_action (
    weekly_action_id    BIGSERIAL PRIMARY KEY,
    scenario_result_id  BIGINT NOT NULL REFERENCES scenario_result (scenario_result_id) ON DELETE CASCADE,
    action_type         VARCHAR(64),
    action_title        VARCHAR(512),
    action_description  TEXT,
    priority_order      INTEGER,
    service_link_id     BIGINT REFERENCES external_service_link (service_link_id)
);

-- §8 CALCULATION_AUDIT_LOG — 테이블명은 기존 엔티티와 맞춰 calculation_log 유지, PK 컬럼명 audit_id
CREATE TABLE calculation_log (
    audit_id           BIGSERIAL PRIMARY KEY,
    simulation_run_id  BIGINT NOT NULL REFERENCES simulation_run (simulation_run_id) ON DELETE CASCADE,
    calculation_type   VARCHAR(64),
    formula_version    TEXT,
    input_hash         TEXT,
    output_hash        TEXT,
    passed_validation  BOOLEAN,
    error_type         VARCHAR(64),
    error_message      TEXT
);

CREATE INDEX idx_calculation_log_run ON calculation_log (simulation_run_id);

-- §7 데이터 계보 (dataset_registry 는 아래 CREATE; 기존 Flyway에 없으면 신규)
CREATE TABLE dataset_registry (
    dataset_id      BIGSERIAL PRIMARY KEY,
    dataset_code    VARCHAR(64)  NOT NULL UNIQUE,
    dataset_name    VARCHAR(512) NOT NULL,
    scope_domain    VARCHAR(64),
    provider        VARCHAR(256),
    source_url      VARCHAR(2048),
    update_cycle    VARCHAR(64),
    is_public_data  BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE TABLE data_source (
    data_source_id   BIGSERIAL PRIMARY KEY,
    dataset_id       BIGINT       NOT NULL REFERENCES dataset_registry (dataset_id) ON DELETE CASCADE,
    source_name      VARCHAR(512),
    source_file_name VARCHAR(512),
    source_type      VARCHAR(64),
    storage_path     VARCHAR(2048),
    base_date        DATE,
    schema_hash      VARCHAR(128)
);

CREATE INDEX idx_data_source_dataset ON data_source (dataset_id);

CREATE TABLE data_snapshot (
    data_snapshot_id    BIGSERIAL PRIMARY KEY,
    data_source_id      BIGINT NOT NULL REFERENCES data_source (data_source_id) ON DELETE CASCADE,
    snapshot_version    VARCHAR(64),
    collected_at        TIMESTAMP,
    row_count           INTEGER,
    missing_value_rate  NUMERIC(14, 6),
    coverage_rate       NUMERIC(14, 6),
    freshness_score     NUMERIC(14, 6),
    data_quality_score  NUMERIC(14, 6),
    schema_hash         VARCHAR(128)
);

CREATE INDEX idx_data_snapshot_source ON data_snapshot (data_source_id);

CREATE TABLE dataset_validation_result (
    validation_result_id BIGSERIAL PRIMARY KEY,
    data_snapshot_id     BIGINT NOT NULL REFERENCES data_snapshot (data_snapshot_id) ON DELETE CASCADE,
    validation_status    VARCHAR(32),
    missing_count        INTEGER,
    invalid_count        INTEGER,
    duplicate_count      INTEGER,
    validation_message   TEXT
);

CREATE TABLE threshold_data_provenance (
    provenance_id         BIGSERIAL PRIMARY KEY,
    threshold_result_id BIGINT NOT NULL REFERENCES threshold_result (threshold_result_id) ON DELETE CASCADE,
    data_snapshot_id      BIGINT NOT NULL REFERENCES data_snapshot (data_snapshot_id),
    used_field            VARCHAR(256),
    calculation_note      TEXT
);

CREATE TABLE simulation_data_usage (
    usage_id           BIGSERIAL PRIMARY KEY,
    simulation_run_id  BIGINT NOT NULL REFERENCES simulation_run (simulation_run_id) ON DELETE CASCADE,
    data_snapshot_id   BIGINT NOT NULL REFERENCES data_snapshot (data_snapshot_id),
    used_for           VARCHAR(128),
    used_field_list    TEXT,
    source_weight      NUMERIC(14, 6)
);

CREATE INDEX idx_simulation_data_usage_run ON simulation_data_usage (simulation_run_id);
