"""MVP DE parser boundary — Spring ↔ FastAPI payload normalize/validate."""

from .normalize import normalize_district_name
from .validate import ValidationError, validate_housing_request

__all__ = [
    "normalize_district_name",
    "validate_housing_request",
    "ValidationError",
]
