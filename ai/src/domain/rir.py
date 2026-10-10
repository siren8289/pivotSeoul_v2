"""RIR(소득 대비 주거비 비율) 계산 규칙.

RIR = 월 주거비 ÷ 월 소득
  - 30% 이하 : 안정 (stable)
  - 40% 이하 : 주의 (warning)
  - 40% 초과 : 위험 (danger) → Red Zone
"""

CONVERSION_RATE = 0.05  # 전월세 전환율 연 5% (data/etl/config.py 와 같은 값)
SAFE_LIMIT = 0.30
RED_ZONE_LIMIT = 0.40


def monthly_cost(deposit, monthly_rent):
    """보증금·월세(만원)를 '월 환산 주거비'(만원)로 바꾼다."""
    return round(monthly_rent + deposit * CONVERSION_RATE / 12, 1)


def calculate_rir(monthly_income, cost):
    """소득이 0 이하면 계산할 수 없으므로 None"""
    if monthly_income <= 0:
        return None
    return round(cost / monthly_income, 4)


def classify(rir):
    """RIR 값으로 상태를 나눈다. (상태, Red Zone 여부)"""
    if rir is None:
        return "unknown", False
    if rir <= SAFE_LIMIT:
        return "stable", False
    if rir <= RED_ZONE_LIMIT:
        return "warning", False
    return "danger", True
