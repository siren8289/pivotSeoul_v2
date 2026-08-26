"""District / life-stage normalization for the MVP payload boundary."""


def normalize_district_name(raw: str) -> str:
    """Strip Seoul prefix variants so Spring and FastAPI share one district grain."""
    s = (raw or "").strip()
    if s.startswith("서울"):
        s = (
            s.replace("서울특별시", "")
            .replace("서울시", "")
            .replace("서울", "")
            .strip()
        )
    return s
