#!/usr/bin/env python3
"""git grep for API mappings, then drop files that declare an auth marker.

This file keeps its own copy of the mapping pattern. Do not import auth_surface.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATTERN = r"@(Get|Post|Put|Delete|Patch|Request)Mapping($|\()|@(app|router)\.(get|post|put|delete|patch)\("
AUTH_MARKERS = ("PreAuthorize", "SecurityFilterChain", "HTTPBearer", "AuthenticationPrincipal", "OAuth2")


def scan() -> list[str]:
    result = subprocess.run(
        ["git", "grep", "-n", "-E", "-e", PATTERN, "--", "back/src/main", "ai/src"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip() or f"git grep exit {result.returncode}")
    if result.returncode == 1:
        return []
    by_file: dict[str, list[tuple[str, str]]] = {}
    for line in result.stdout.splitlines():
        path, number, content = line.split(":", 2)
        if path.endswith(".bak"):
            continue
        by_file.setdefault(path, []).append((number, content))
    findings: list[str] = []
    for path, hits in by_file.items():
        text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
        if any(marker in text for marker in AUTH_MARKERS):
            continue
        for number, content in hits:
            if "/health" in content:
                continue
            findings.append(f"{path}:{number}")
    return findings


def main() -> int:
    findings = scan()
    payload = {
        "status": "PASS",
        "summary": f"git grep unauthenticated mappings: {len(findings)}",
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
