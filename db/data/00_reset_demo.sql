-- demo-* 세션 트리만 제거 (CASCADE로 user_condition, scenario, run, result 등)
DELETE FROM simulation_session
WHERE session_uuid LIKE 'demo-%';
