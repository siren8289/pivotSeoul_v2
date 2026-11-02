#!/usr/bin/env python3
"""Security path A: Semgrep static analysis when installed; otherwise BLOCKED (not PASS)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = ["ai/src", "back/src/main", "front/src", "data"]


def main() -> int:
    if not shutil.which("semgrep"):
        payload = {
            "status": "BLOCKED",
            "summary": "semgrep CLI 없음. CI semgrep job 또는 로컬 설치 필요.",
            "findings": ["semgrep:not-installed"],
            "file": "qa/tools/semgrep_check.py",
            "function": "main",
            "line_needle": "def main",
        }
        json.dump(payload, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0

    command = [
        "semgrep",
        "--config=p/ci",
        "--quiet",
        "--json",
        "--error",
        *[str(ROOT / target) for target in TARGETS if (ROOT / target).exists()],
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, timeout=300)
    findings: list[str] = []
    try:
        data = json.loads(completed.stdout or "{}")
        for item in data.get("results", []):
            path = item.get("path", "UNKNOWN")
            line = (item.get("start") or {}).get("line", "?")
            check_id = item.get("check_id", "rule")
            findings.append(f"{path}:{line}:{check_id}")
    except json.JSONDecodeError:
        if completed.returncode not in (0, 1):
            payload = {
                "status": "ERROR",
                "summary": f"semgrep exit {completed.returncode}",
                "findings": [],
                "file": "qa/tools/semgrep_check.py",
                "function": "main",
                "line_needle": "def main",
            }
            json.dump(payload, sys.stdout, ensure_ascii=False)
            sys.stdout.write("\n")
            return 0

    # Semgrep exit 1 = findings; treat high-signal only as FAIL. Presence of results = FAIL for gate honesty.
    status = "FAIL" if findings else "PASS"
    if completed.returncode not in (0, 1):
        status = "ERROR"
    payload = {
        "status": status,
        "summary": f"semgrep findings={len(findings)} exit={completed.returncode}",
        "findings": findings[:50],
        "file": "qa/tools/semgrep_check.py",
        "function": "main",
        "line_needle": "def main",
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
