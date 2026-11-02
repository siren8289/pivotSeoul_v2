#!/usr/bin/env python3
"""Second unit tool for the rent-preprocessing invariants.

Scope is narrower than pytest data/tests: monthly cost formula, empty address,
and as_list. It does not load CSV fixtures or clean_rent.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from data.etl.fetch import as_list  # noqa: E402
from data.etl.transform import calc_monthly_cost, district_from_address  # noqa: E402


def main() -> int:
    failures: list[str] = []

    def expect(name: str, got: object, want: object) -> None:
        if got != want:
            failures.append(f"{name}: got {got!r} want {want!r}")

    expect("jeonse", round(calc_monthly_cost(10000, 0), 2), 41.67)
    expect("wolse", round(calc_monthly_cost(2000, 50), 2), round(50 + 2000 * 0.05 / 12, 2))
    expect("zeros", calc_monthly_cost(0, 0), 0)
    expect("empty-address", district_from_address(""), None)
    expect("null-address", district_from_address(None), None)
    expect("district", district_from_address("서울특별시 마포구 공덕동"), "마포구")
    expect("as-list-none", as_list(None), [])
    expect("as-list-dict", as_list({"a": 1}), [{"a": 1}])
    expect("as-list-list", as_list([1, 2]), [1, 2])

    payload = {
        "status": "FAIL" if failures else "PASS",
        "summary": "invariant mismatches: " + ", ".join(failures) if failures else "9 invariants held",
        "findings": failures,
        "file": "data/etl/transform.py",
        "function": "calc_monthly_cost",
        "line_needle": "def calc_monthly_cost",
    }
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - tool boundary reports the crash
        json.dump({"status": "ERROR", "summary": str(error), "findings": []}, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        raise SystemExit(1)
