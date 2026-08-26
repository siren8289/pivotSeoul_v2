-- =============================================================================
-- 시뮬레이션 확장 테이블 — 스텁 (임시)
-- =============================================================================
-- 목적: JPA 엔티티(ThresholdResult, RedZoneRule 등)가 ddl-auto=validate일 때
--       테이블 존재만 만족시키기 위한 최소 스키마이다.
-- 다음 단계: ERD v4 주거/임계점/추천 등에 맞춰 컬럼·FK·인덱스를 채운 마이그레이션으로 교체·확장한다.
-- 참고: §9 구현 우선순위 2~8, THRESHOLD_RESULT / RECOVERY_LEVER / WEEKLY_ACTION 등
-- =============================================================================

/* 임계점 판정 결과 — scenario_result와 연결 예정 (FK는 추후 마이그레이션에서 정의) */
CREATE TABLE threshold_result (
    id BIGSERIAL PRIMARY KEY
);

/* Red Zone 트리거 규칙 — threshold_type별 조건 */
CREATE TABLE red_zone_rule (
    id BIGSERIAL PRIMARY KEY
);

/* 회복 레버(이동·예산·정책 등) 제안 — threshold_result와 연결 예정 */
CREATE TABLE recovery_lever (
    id BIGSERIAL PRIMARY KEY
);

/* 이번 주 실행 액션 — 시나리오 결과와 연결 예정 */
CREATE TABLE weekly_action (
    id BIGSERIAL PRIMARY KEY
);

/* 계산 감사 로그 — 수식 버전·입출력 해시 등 (CALCULATION_AUDIT_LOG 개념과 정렬 예정) */
CREATE TABLE calculation_log (
    id BIGSERIAL PRIMARY KEY
);
