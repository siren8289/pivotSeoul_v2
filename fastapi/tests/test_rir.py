from housing.rir import (
    calculate_rir,
    classify_housing_status,
    calculate_housing_risk_score,
)


def test_prd_acceptance_rir_red_zone() -> None:
    """FR-003: 월소득 500만, 주거비 225만 → RIR=0.45, red zone, danger."""
    rir = calculate_rir(5_000_000, 2_250_000)
    status, is_red_zone = classify_housing_status(rir)

    assert rir == 0.45
    assert is_red_zone is True
    assert status == "danger"
    assert calculate_housing_risk_score(rir) == 80


def test_rir_warning_at_threshold() -> None:
    rir = calculate_rir(5_000_000, 2_000_000)
    status, is_red_zone = classify_housing_status(rir)

    assert rir == 0.4
    assert is_red_zone is False
    assert status == "warning"


def test_rir_stable_below_30_percent() -> None:
    rir = calculate_rir(5_000_000, 1_000_000)
    status, is_red_zone = classify_housing_status(rir)

    assert rir == 0.2
    assert is_red_zone is False
    assert status == "stable"


def test_rir_none_when_income_invalid() -> None:
    assert calculate_rir(0, 1_000_000) is None
    assert calculate_rir(None, 1_000_000) is None
