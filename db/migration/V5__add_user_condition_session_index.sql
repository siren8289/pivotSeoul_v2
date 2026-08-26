-- =============================================================================
-- ERD v5 user condition lookup index
-- =============================================================================
-- V4 creates user_condition. Keep V5 additive so Flyway can run on both fresh and
-- already-initialized databases without trying to create the table twice.
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_user_condition_session ON user_condition (session_id);
