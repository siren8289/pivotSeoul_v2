# FastAPI — MVP RIR 엔진

```
fastapi/
  main.py           # FastAPI 앱 + /health
  housing/          # 주거(RIR) 도메인
    router.py
    service.py
    schema.py
    rir.py
    preprocessing.py
    result_builder.py
```

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
pytest
```

Spring Back은 `POST /api/v1/housing/analyze` 를 내부 호출합니다.

PRD 수용 기준: 월소득 5,000,000원 / 주거비 2,250,000원 → `rir=0.45`, `is_red_zone=true`, `housing_status=danger`.
