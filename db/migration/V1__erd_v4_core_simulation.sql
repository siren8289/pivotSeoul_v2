-- =============================================================================
-- ERD v4 §1 — 공통 시뮬레이션 (Phase 1)
-- =============================================================================
-- 목적: 사용자 1회 실행 단위(session) · A/B 시나리오 · 실행(run) · 시나리오별 결과를 저장.
-- 원칙: 원본 입력값은 저장하지 않고 scenario_input_summary에 구간화 요약만 둔다.
-- 참고: docs/ERD-v4-feature-based.md, back/STRUCTURE.md domain/simulation
-- =============================================================================

/* 생애 단계 마스터 — 온보딩에서 선택 가능한 단계 정의 */
CREATE TABLE life_stage (
    life_stage_id BIGSERIAL PRIMARY KEY,
    stage_code    VARCHAR(32)  NOT NULL UNIQUE, -- 비즈니스 코드 (예: YOUTH, FAMILY)
    stage_name    VARCHAR(128) NOT NULL,
    description   TEXT
);

/* 서울 자치구 등 비교·표시용 행정구역 */
CREATE TABLE district (
    district_id   BIGSERIAL PRIMARY KEY,
    district_code VARCHAR(16) NOT NULL UNIQUE, -- 공공데이터 등과 매칭할 코드
    district_name VARCHAR(64) NOT NULL,
    region_group  VARCHAR(64)                  -- 권역 묶음 (UX/필터용)
);

/*
 * 시뮬레이션 세션 — 계정 중심이 아니라 "한 번의 시뮬 실행" 단위.
 * anonymous_user_key_hash: 로그인 없이 동일 사용자 추적·중복 완화 등에 사용 가능 (해시만 저장).
 */
CREATE TABLE simulation_session (
    session_id                  BIGSERIAL PRIMARY KEY,
    session_uuid                VARCHAR(64) NOT NULL UNIQUE, -- 클라이언트·API 상관관계 ID
    life_stage_id               BIGINT       NOT NULL REFERENCES life_stage (life_stage_id),
    anonymous_user_key_hash     VARCHAR(128),
    session_status              VARCHAR(32)  NOT NULL, -- 예: DRAFT, READY, CLOSED
    consent_to_save_result      BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at                  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expired_at                  TIMESTAMP                             -- TTL·개인정보 정책용
);

CREATE INDEX idx_simulation_session_life_stage ON simulation_session (life_stage_id);

/*
 * 시나리오 — 세션 내 A/B 각각 한 행.
 * scenario_type: 'A' | 'B' 등 비교 축 구분.
 * current_district_id / compare_district_id: 주거·통근 비교 등 지역 조건.
 */
CREATE TABLE scenario (
    scenario_id           BIGSERIAL PRIMARY KEY,
    session_id            BIGINT       NOT NULL REFERENCES simulation_session (session_id) ON DELETE CASCADE,
    scenario_type         VARCHAR(16)  NOT NULL,
    current_district_id   BIGINT REFERENCES district (district_id),
    compare_district_id   BIGINT REFERENCES district (district_id),
    scenario_title        VARCHAR(256),
    display_order         INTEGER                               -- UI 나열 순서
);

CREATE INDEX idx_scenario_session ON scenario (scenario_id);

/*
 * 입력 요약 — 개인정보 최소화: 원값 대신 구간/밴드만 저장 (ERD v4 설계 원칙).
 * 시나리오당 1행 (UNIQUE scenario_id).
 */
CREATE TABLE scenario_input_summary (
    input_summary_id    BIGSERIAL PRIMARY KEY,
    scenario_id         BIGINT       NOT NULL UNIQUE REFERENCES scenario (scenario_id) ON DELETE CASCADE,
    age_group           VARCHAR(64),
    income_band         VARCHAR(64),
    household_type      VARCHAR(64),
    child_age_group     VARCHAR(64),
    target_job_group    VARCHAR(128),
    monthly_budget_band VARCHAR(64),
    is_anonymized       BOOLEAN      NOT NULL DEFAULT TRUE
);

/*
 * 시뮬레이션 실행 — 세션당 여러 번 재실행 가능.
 * calculation_engine_version / ai_pipeline_version: 재현성·감사 추적용.
 */
CREATE TABLE simulation_run (
    simulation_run_id           BIGSERIAL PRIMARY KEY,
    session_id                  BIGINT NOT NULL REFERENCES simulation_session (session_id) ON DELETE CASCADE,
    run_status                  VARCHAR(32) NOT NULL, -- 예: RUNNING, SUCCEEDED, FAILED
    calculation_engine_version  VARCHAR(64),
    ai_pipeline_version         VARCHAR(64),
    total_confidence_score      NUMERIC(14, 6),
    started_at                  TIMESTAMP,
    completed_at                TIMESTAMP
);

CREATE INDEX idx_simulation_run_session ON simulation_run (session_id);

/*
 * 시나리오 결과 — 한 run 안에서 시나리오별 집계 점수·상태.
 * 이후 주거/커리어 등 도메인 점수 컬럼은 Phase별 마이그레이션으로 확장 가능.
 */
CREATE TABLE scenario_result (
    scenario_result_id BIGSERIAL PRIMARY KEY,
    simulation_run_id  BIGINT NOT NULL REFERENCES simulation_run (simulation_run_id) ON DELETE CASCADE,
    scenario_id        BIGINT NOT NULL REFERENCES scenario (scenario_id) ON DELETE CASCADE,
    result_status      VARCHAR(32),
    total_score        NUMERIC(14, 6),
    risk_score         NUMERIC(14, 6),
    confidence_score   NUMERIC(14, 6)
);

CREATE INDEX idx_scenario_result_run ON scenario_result (simulation_run_id);
CREATE INDEX idx_scenario_result_scenario ON scenario_result (scenario_id);

/*
 * A/B 비교 — 한 run에서 두 scenario_result를 묶어 차이·추천 축 저장.
 */
CREATE TABLE scenario_comparison (
    comparison_id              BIGSERIAL PRIMARY KEY,
    simulation_run_id          BIGINT NOT NULL REFERENCES simulation_run (simulation_run_id) ON DELETE CASCADE,
    base_scenario_result_id    BIGINT NOT NULL REFERENCES scenario_result (scenario_result_id) ON DELETE CASCADE,
    compare_scenario_result_id BIGINT NOT NULL REFERENCES scenario_result (scenario_result_id) ON DELETE CASCADE,
    score_diff                 NUMERIC(14, 6),
    risk_diff                  NUMERIC(14, 6),
    recommended_scenario_type  VARCHAR(16), -- 예: A 또는 B 권장
    comparison_summary         TEXT         -- 요약 텍스트 (LLM 아님 저장 가능)
);

CREATE INDEX idx_scenario_comparison_run ON scenario_comparison (simulation_run_id);
