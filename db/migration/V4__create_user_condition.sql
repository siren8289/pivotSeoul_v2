-- =============================================================================
-- ERD v4 UserCondition 테이블 생성
-- =============================================================================
CREATE TABLE user_condition (
    user_condition_id      BIGSERIAL PRIMARY KEY,
    session_id             BIGINT NOT NULL UNIQUE REFERENCES simulation_session (session_id) ON DELETE CASCADE,
    current_district       VARCHAR(64),
    compare_district       VARCHAR(64),
    monthly_income         INTEGER,
    monthly_housing        INTEGER,
    monthly_living         INTEGER,
    commute_time           INTEGER,
    childcare_cost         INTEGER,
    return_to_work_months  INTEGER,
    retirement_age         INTEGER,
    savings                INTEGER,
    created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);