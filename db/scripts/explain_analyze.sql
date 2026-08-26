-- §0·§3 실행계획 확인 — MVP 핵심 쿼리 EXPLAIN ANALYZE
-- Usage: psql -f db/scripts/explain_analyze.sql

\echo '=== F-003 getResult (JOIN 1회) ==='
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT sr.scenario_result_id,
       sr.simulation_run_id,
       sr.scenario_id,
       sr.result_status,
       sr.total_score,
       sr.risk_score,
       sr.confidence_score,
       sr.housing_score,
       tr.threshold_result_id,
       tr.threshold_type_id,
       tr.threshold_status,
       tr.calculated_value,
       tr.threshold_value,
       tr.is_red_zone,
       tr.calculation_summary
FROM scenario_result sr
LEFT JOIN threshold_result tr ON tr.scenario_result_id = sr.scenario_result_id
WHERE sr.scenario_result_id = (
    SELECT scenario_result_id
    FROM scenario_result
    ORDER BY scenario_result_id DESC
    LIMIT 1
)
ORDER BY tr.threshold_result_id ASC NULLS LAST;

\echo '=== F-002 scenario lookup by session ==='
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT scenario_id, session_id, scenario_type, display_order
FROM scenario
WHERE session_id = (SELECT session_id FROM simulation_session ORDER BY session_id DESC LIMIT 1)
ORDER BY display_order, scenario_id;

\echo '=== session_uuid lookup ==='
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT session_id, session_uuid, session_status
FROM simulation_session
WHERE session_uuid = 'demo-ready-001';

\echo '=== analytics mart refresh source ==='
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT r.simulation_run_id,
       r.session_id,
       sr.scenario_result_id,
       tr.calculated_value,
       tr.is_red_zone,
       sr.risk_score
FROM simulation_run r
JOIN scenario_result sr ON sr.simulation_run_id = r.simulation_run_id
LEFT JOIN threshold_result tr ON tr.scenario_result_id = sr.scenario_result_id
WHERE r.run_status = 'COMPLETED'
ORDER BY r.completed_at DESC
LIMIT 100;
