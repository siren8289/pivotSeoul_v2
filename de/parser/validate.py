"""Request/response contract checks at the Spring–FastAPI parser boundary."""

from __future__ import annotations

from typing import Any, Mapping


class ValidationError(ValueError):
    """Raised when a housing analyze payload fails MVP contract rules."""


REQUIRED_REQUEST_FIELDS = ("district",)


def validate_housing_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    """
    Validate MVP housing analyze request fields.

    Checks schema compatibility essentials from the DE contract:
    required fields, non-empty district, and non-negative numeric ranges.
    """
    if not isinstance(payload, Mapping):
        raise ValidationError("payload must be an object")

    missing = [f for f in REQUIRED_REQUEST_FIELDS if f not in payload or payload[f] in (None, "")]
    if missing:
        raise ValidationError(f"missing required fields: {', '.join(missing)}")

    district = str(payload["district"]).strip()
    if not district:
        raise ValidationError("district must be a non-empty string")

    monthly_income = payload.get("monthly_income")
    monthly_housing_cost = payload.get("monthly_housing_cost")

    for name, value in (
        ("monthly_income", monthly_income),
        ("monthly_housing_cost", monthly_housing_cost),
    ):
        if value is None:
            continue
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValidationError(f"{name} must be a number")
        if value < 0:
            raise ValidationError(f"{name} must be >= 0")

    return {
        "district": district,
        "monthly_income": None if monthly_income is None else int(monthly_income),
        "monthly_housing_cost": (
            None if monthly_housing_cost is None else int(monthly_housing_cost)
        ),
    }
