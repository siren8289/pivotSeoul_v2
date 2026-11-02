#!/usr/bin/env python3
"""Second compose verifier: greps required service anchors (tool B for infra)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ROOT / "compose.yaml"
ANCHORS = (
    ("db", r"(?m)^  db:\s*$"),
    ("ai", r"(?m)^  ai:\s*$"),
    ("back", r"(?m)^  back:\s*$"),
    ("front", r"(?m)^  front:\s*$"),
    ("pgvector", r"pgvector/pgvector:pg16"),
    ("db-data", r"db-data:"),
)


def main() -> int:
    findings: list[str] = []
    if not COMPOSE.is_file():
        findings.append("compose.yaml:missing")
    else:
        text = COMPOSE.read_text(encoding="utf-8")
        for label, pattern in ANCHORS:
            if not re.search(pattern, text):
                findings.append(f"missing-anchor:{label}")
        if "DB_PASSWORD" not in text:
            findings.append("missing-anchor:DB_PASSWORD")
    status = "FAIL" if findings else "PASS"
    payload = {
        "status": status,
        "summary": f"anchors checked={len(ANCHORS)+1} findings={len(findings)}",
        "findings": findings,
        "file": "compose.yaml",
        "function": "services",
        "line_needle": "services:",
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
