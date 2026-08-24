"""MVP RIR AI 엔진 — Spring Back이 내부 호출합니다."""

from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from housing.router import router as housing_router

app = FastAPI(
    title="Pivot Seoul API",
    version="0.2.0-mvp",
    description="MVP 주거(RIR) 분석 AI 엔진",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(housing_router, prefix="/api/v1")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "fastapi"}


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "Pivot Seoul AI 엔진이 작동 중입니다."}
