"""pivotSeoul AI 서버 (FastAPI). Spring 백엔드가 내부에서 호출한다.

POST /api/v1/diagnose   내 주거비 진단
POST /api/v1/recommend  예산에 맞는 자치구 추천
"""
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.service import diagnose, recommend

app = FastAPI(title="pivotSeoul AI", version="2.0.0")

LifeStage = Literal["youth", "family", "senior"]
# apartment=아파트, officetel=오피스텔, house=단독/다가구, villa=연립/다세대
HouseType = Literal["apartment", "officetel", "house", "villa"]


class DiagnoseRequest(BaseModel):
    life_stage: LifeStage = "youth"
    district: str = Field(examples=["마포구"])
    house_type: HouseType = "apartment"
    area_m2: float = Field(gt=5, le=300, description="전용면적(㎡)")
    building_age: int = Field(default=15, ge=0, le=60, description="건물 나이(년)")
    floor: int = Field(default=5, ge=0, le=80)
    monthly_income: float = Field(gt=0, description="월 소득(만원)")
    deposit: float = Field(ge=0, description="보증금(만원)")
    monthly_rent: float = Field(ge=0, description="월세(만원)")


class RecommendRequest(BaseModel):
    life_stage: LifeStage = "youth"
    house_type: HouseType = "apartment"
    area_m2: float = Field(gt=5, le=300)
    building_age: int = Field(default=15, ge=0, le=60)
    floor: int = Field(default=5, ge=0, le=80)
    monthly_income: float = Field(gt=0)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/diagnose")
def diagnose_api(request: DiagnoseRequest):
    return diagnose(request.model_dump())


@app.post("/api/v1/recommend")
def recommend_api(request: RecommendRequest):
    return recommend(request.model_dump())
