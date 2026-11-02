#!/usr/bin/env python3
"""Infra path B: curl-class HTTP smoke against local health endpoints. BLOCKED if services down."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENDPOINTS = [
    ("front", "http://127.0.0.1/"),
    ("back_health", "http://127.0.0.1:8080/actuator/health"),
    ("back_health_alt", "http://127.0.0.1:8080/health"),
    ("ai_health", "http://127.0.0.1:8000/health"),
]


def probe(url: str, timeout: float = 2.0) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return True, f"{response.status}"
    except urllib.error.HTTPError as error:
        return True, f"HTTPError:{error.code}"
    except Exception as error:  # noqa: BLE001
        return False, str(error)


def main() -> int:
    findings: list[str] = []
    reached = 0
    for name, url in ENDPOINTS:
        ok, detail = probe(url)
        if ok:
            reached += 1
        else:
            findings.append(f"{name}:down:{detail}")

    if reached == 0:
        status = "BLOCKED"
        summary = "로컬 서비스가 응답하지 않음. compose up 후 재실행하거나 CI smoke job 사용."
    elif reached < 2:
        status = "FAIL"
        summary = f"일부 엔드포인트만 응답 reached={reached}"
    else:
        status = "PASS"
        summary = f"HTTP smoke reached={reached}"

    payload = {
        "status": status,
        "summary": summary,
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
