from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class HousingRequest(BaseModel):
    district: str
    monthly_income: Optional[int] = Field(default=None, ge=0)
    monthly_housing_cost: Optional[int] = Field(default=None, ge=0)


class HousingResult(BaseModel):
    district: str
    monthly_income: Optional[int] = None
    monthly_housing_cost: Optional[int] = None
    rir: Optional[float] = None
    housing_status: str = "pending"
    is_red_zone: bool = False
    risk_score: Optional[int] = None
    confidence_score: Optional[float] = None
