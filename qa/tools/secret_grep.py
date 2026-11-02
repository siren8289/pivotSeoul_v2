#!/usr/bin/env python3
"""git grep for the same high-confidence secret patterns as secret_scan.py.

This file keeps its own copy of the pattern. Do not import secret_scan.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATTERN = r"-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_\-]{35}|ghp_[A-Za-z0-9]{36}"


def scan() -> list[str]:
    result = subprocess.run(
        ["git", "grep", "-n", "-I", "-E", "-e", PATTERN, "--", "."],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip() or f"git grep exit {result.returncode}")
    if result.returncode == 1:
        return []
    findings: list[str] = []
    for line in result.stdout.splitlines():
        path, number, _content = line.split(":", 2)
        findings.append(f"{path}:{number}")
    return findings


def main() -> int:
    findings = scan()
    payload = {
        "status": "FAIL" if findings else "PASS",
        "summary": f"git grep secret findings: {len(findings)}",
        "findings": findings,
        "file": "qa/tools/secret_grep.py",
        "function": "scan",
        "line_needle": "def scan",
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
