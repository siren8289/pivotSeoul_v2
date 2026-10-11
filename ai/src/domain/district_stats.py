"""자치구별 통계(data 파이프라인 결과)를 읽어 온다."""
import json
from pathlib import Path

STATS_PATH = Path(__file__).resolve().parents[2] / "models" / "district_stats.json"

_stats = None


def load_stats():
    """[{district, house_type, deal_count, median_monthly_cost, ...}, ...]"""
    global _stats
    if _stats is None:
        _stats = json.loads(STATS_PATH.read_text(encoding="utf-8"))
    return _stats


def find_stat(district, house_type):
    for row in load_stats():
        if row["district"] == district and row["house_type"] == house_type:
            return row
    return None


def all_districts():
    return sorted({row["district"] for row in load_stats()})
