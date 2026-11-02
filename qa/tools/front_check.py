#!/usr/bin/env python3
"""Second tool for QA-UNIT-FRONT-001.

Independently inspects front/src/components/options.ts, front/src/api/api.ts,
front/src/App.tsx, and front/src/pages/*.tsx without using Node.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    failures: list[str] = []

    options_path = ROOT / "front" / "src" / "components" / "options.ts"
    api_path = ROOT / "front" / "src" / "api" / "api.ts"
    app_path = ROOT / "front" / "src" / "App.tsx"
    diagnose_path = ROOT / "front" / "src" / "pages" / "DiagnosePage.tsx"
    recommend_path = ROOT / "front" / "src" / "pages" / "RecommendPage.tsx"
    result_path = ROOT / "front" / "src" / "pages" / "ResultPage.tsx"
    pkg_path = ROOT / "front" / "package.json"

    for p in (options_path, api_path, app_path, diagnose_path, recommend_path, result_path, pkg_path):
        if not p.is_file():
            failures.append(f"missing file: {p.relative_to(ROOT)}")

    if not failures:
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
        if "test" not in pkg.get("scripts", {}):
            failures.append("front/package.json missing test script")

        opt_text = options_path.read_text(encoding="utf-8")
        districts = re.findall(r'"([가-힣]+구)"', opt_text)
        if len(districts) != 25 or len(set(districts)) != 25:
            failures.append(f"expected 25 unique districts, got {len(districts)} ({len(set(districts))} unique)")
        for stage in ("youth", "family", "senior"):
            if f'value: "{stage}"' not in opt_text:
                failures.append(f"missing lifeStage {stage}")
        for htype in ("apartment", "officetel", "house", "villa"):
            if f'value: "{htype}"' not in opt_text:
                failures.append(f"missing houseType {htype}")
        for status_key in ("stable", "warning", "danger", "unknown"):
            if f"{status_key}:" not in opt_text:
                failures.append(f"missing STATUS_INFO key {status_key}")

        api_text = api_path.read_text(encoding="utf-8")
        for endpoint in ('"/api/diagnoses"', '`/api/diagnoses/${id}`', '"/api/recommendations"'):
            if endpoint not in api_text:
                failures.append(f"front/src/api/api.ts missing endpoint {endpoint}")

        app_text = app_path.read_text(encoding="utf-8")
        for route in ('path="/"', 'path="/recommend"', 'path="/diagnoses/:id"'):
            if route not in app_text:
                failures.append(f"front/src/App.tsx missing route {route}")

        diag_text = diagnose_path.read_text(encoding="utf-8")
        rec_text = recommend_path.read_text(encoding="utf-8")
        res_text = result_path.read_text(encoding="utf-8")
        if "Number(monthlyIncome) <= 0" not in diag_text:
            failures.append("DiagnosePage missing monthlyIncome <= 0 guard")
        if "Number(monthlyIncome) <= 0" not in rec_text:
            failures.append("RecommendPage missing monthlyIncome <= 0 guard")
        if "STATUS_INFO[result.status] ?? STATUS_INFO.unknown" not in res_text:
            failures.append("ResultPage missing STATUS_INFO fallback")

    payload = {
        "status": "FAIL" if failures else "PASS",
        "summary": ", ".join(failures) if failures else "front options(25 districts), routes, API endpoints, and guards verified",
        "findings": failures,
        "file": "front/src/components/options.ts",
        "function": "DISTRICTS",
        "line_needle": "export const DISTRICTS",
    }
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001
        json.dump({"status": "ERROR", "summary": str(error), "findings": []}, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        raise SystemExit(1)
