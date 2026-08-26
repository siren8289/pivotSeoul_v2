-- MVP seed: life stages + HOUSING threshold type
INSERT INTO life_stage (stage_code, stage_name, description)
VALUES
    ('YOUTH', '청년기', '20-35세'),
    ('FAMILY', '신혼·출산기', '30-45세'),
    ('SENIOR', '노년기', '55세 이상')
ON CONFLICT (stage_code) DO NOTHING;

INSERT INTO threshold_type (threshold_code, threshold_name, formula_version, unit_default)
VALUES ('HOUSING', '주거비 부담률(RIR)', 'RIR_V1', 'ratio')
ON CONFLICT (threshold_code) DO NOTHING;
