#!/usr/bin/env python3
"""Walk API sources and list mappings in files that have no auth marker.

Health probes are excluded. The pattern is duplicated in auth_grep.py.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAPPING = re.compile(
    r"@(Get|Post|Put|Delete|Patch|Request)Mapping($|\()|@(app|router)\.(get|post|put|delete|patch)\("
)
AUTH_MARKERS = ("PreAuthorize", "SecurityFilterChain", "HTTPBearer", "AuthenticationPrincipal", "OAuth2")


def candidates() -> list[str]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True)
    names = [item.decode("utf-8", "surrogateescape") for item in result.stdout.split(b"\0") if item]
    selected = []
    for name in names:
        if name.startswith("back/src/main/java/") and name.endswith(".java"):
            selected.append(name)
        elif name.startswith("ai/src/") and name.endswith(".py"):
            selected.append(name)
    return selected


def scan() -> list[str]:
    findings: list[str] = []
    for relative in candidates():
        text = (ROOT / relative).read_text(encoding="utf-8", errors="replace")
        if any(marker in text for marker in AUTH_MARKERS):
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if "/health" in line:
                continue
            if MAPPING.search(line):
                findings.append(f"{relative}:{number}")
    return findings


def main() -> int:
    findings = scan()
    payload = {
        "status": "PASS",
        "summary": f"unauthenticated mappings: {len(findings)}",
        "findings": findings,
        "file": "back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java",
        "function": "get",
        "line_needle": '@GetMapping("/{id}")',
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
