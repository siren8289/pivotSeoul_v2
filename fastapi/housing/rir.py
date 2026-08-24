from __future__ import annotations

from typing import Optional, Tuple


def calculate_rir(monthly_income: Optional[int], monthly_housing_cost: Optional[int]) -> Optional[float]:
    """RIR = 월 주거비 / 월 소득"""
    if monthly_income is None or monthly_housing_cost is None:
        return None
    if monthly_income <= 0:
        return None
    return round(monthly_housing_cost / monthly_income, 4)


def classify_housing_status(rir: Optional[float]) -> Tuple[str, bool]:
    if rir is None:
        return "unknown", False
    if rir <= 0.30:
        return "stable", False
    if rir <= 0.40:
        return "warning", False
    return "danger", True


def calculate_housing_risk_score(rir: Optional[float]) -> int:
    if rir is None:
        return 0
    if rir <= 0.30:
        return 20
    if rir <= 0.40:
        return 50
    return 80


def calculate_confidence_score(rir: Optional[float]) -> float:
    if rir is None:
        return 0.3
    return 0.85
