#!/usr/bin/env python3
"""Walk tracked files for high-confidence secret patterns.

The pattern is duplicated in secret_grep.py on purpose. The two tools must not
import a shared scanner.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATTERN = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_\-]{35}|ghp_[A-Za-z0-9]{36}"
)
SKIP_SUFFIXES = {".pt", ".joblib", ".jar", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".zip", ".woff", ".woff2"}


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [item.decode("utf-8", "surrogateescape") for item in result.stdout.split(b"\0") if item]


def scan() -> list[str]:
    findings: list[str] = []
    for relative in tracked_files():
        path = ROOT / relative
        if path.suffix.lower() in SKIP_SUFFIXES or not path.is_file():
            continue
        data = path.read_bytes()
        if b"\0" in data[:1024] or len(data) > 1_000_000:
            continue
        text = data.decode("utf-8", "replace")
        for number, line in enumerate(text.splitlines(), 1):
            if PATTERN.search(line):
                findings.append(f"{relative}:{number}")
    return findings


def main() -> int:
    findings = scan()
    payload = {
        "status": "FAIL" if findings else "PASS",
        "summary": f"secret findings: {len(findings)}",
        "findings": findings,
        "file": "qa/tools/secret_scan.py",
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
