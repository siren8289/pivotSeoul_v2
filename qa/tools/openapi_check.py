#!/usr/bin/env python3
"""Independent API surface check (Schemathesis-class path without live server).

Tries FastAPI openapi() when importable; otherwise statically verifies route
decorators and Spring controllers so the QA venv does not require ai deps.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AI_SRC = ROOT / "ai" / "src"
BACK = ROOT / "back" / "src" / "main" / "java"


def try_fastapi_openapi() -> tuple[str | None, list[str]]:
    sys.path.insert(0, str(AI_SRC))
    try:
        from api.main import app  # type: ignore

        schema = app.openapi()
        paths = list((schema.get("paths") or {}).keys())
        findings: list[str] = []
        if len(paths) < 2:
            findings.append(f"openapi:too-few-paths:{len(paths)}")
        if "schemas" not in (schema.get("components") or {}):
            findings.append("openapi:no-component-schemas")
        return f"openapi_paths={len(paths)}", findings
    except Exception as error:  # noqa: BLE001
        return None, [f"fastapi_import:{error}"]


def static_fastapi_routes() -> tuple[int, list[str]]:
    findings: list[str] = []
    if not AI_SRC.exists():
        return 0, ["ai_src:missing"]
    route_re = re.compile(r"@(app|router)\.(get|post|put|delete|patch)\(\s*[\"']([^\"']+)[\"']")
    count = 0
    for path in AI_SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        count += len(route_re.findall(text))
    if count < 2:
        findings.append(f"static_routes:too-few:{count}")
    return count, findings


def spring_controllers() -> tuple[int, list[str]]:
    findings: list[str] = []
    if not BACK.exists():
        return 0, ["spring:missing"]
    controllers = list(BACK.rglob("*Controller.java"))
    if not controllers:
        findings.append("spring:no-controllers")
    mapping_re = re.compile(r"@(Get|Post|Put|Delete|Patch|Request)Mapping")
    mapped = 0
    for path in controllers:
        mapped += len(mapping_re.findall(path.read_text(encoding="utf-8", errors="replace")))
    if mapped < 1:
        findings.append("spring:no-mappings")
    return len(controllers), findings


def main() -> int:
    summary_bits: list[str] = []
    findings: list[str] = []

    openapi_summary, openapi_findings = try_fastapi_openapi()
    if openapi_summary:
        summary_bits.append(openapi_summary)
        findings.extend([f for f in openapi_findings if not f.startswith("fastapi_import")])
    else:
        routes, static_findings = static_fastapi_routes()
        summary_bits.append(f"static_routes={routes}")
        findings.extend(static_findings)
        # import failure alone is not FAIL if static routes exist
        if routes >= 2:
            findings = [f for f in findings if not f.startswith("fastapi_import")]

    controllers, spring_findings = spring_controllers()
    summary_bits.append(f"controllers={controllers}")
    findings.extend(spring_findings)

    hard = [f for f in findings if f.startswith(("openapi:too-", "openapi:no-", "static_routes:", "spring:"))]
    status = "FAIL" if hard else "PASS"
    payload = {
        "status": status,
        "summary": " ".join(summary_bits) + f" findings={len(findings)}",
        "findings": findings,
        "file": "ai/src/api/main.py",
        "function": "app",
        "line_needle": "app = FastAPI",
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
