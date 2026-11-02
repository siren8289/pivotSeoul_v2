#!/usr/bin/env python3
"""Static compose.yaml service/build/health structure check (tool A for infra)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ROOT / "compose.yaml"
REQUIRED = ("db", "ai", "back", "front")


def parse_services(text: str) -> dict[str, dict[str, bool]]:
    services: dict[str, dict[str, bool]] = {}
    current: str | None = None
    in_services = False
    for raw in text.splitlines():
        if re.match(r"^services:\s*$", raw):
            in_services = True
            continue
        if not in_services:
            continue
        if re.match(r"^[A-Za-z0-9_]+:\s*$", raw) and not raw.startswith(" "):
            break
        top = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", raw)
        if top:
            current = top.group(1)
            services[current] = {"image": False, "build": False, "healthcheck": False, "depends_on": False}
            continue
        if current is None:
            continue
        if re.match(r"^    image:\s*", raw):
            services[current]["image"] = True
        elif re.match(r"^    build:\s*", raw):
            services[current]["build"] = True
        elif re.match(r"^    healthcheck:\s*$", raw):
            services[current]["healthcheck"] = True
        elif re.match(r"^    depends_on:\s*$", raw):
            services[current]["depends_on"] = True
    return services


def main() -> int:
    findings: list[str] = []
    if not COMPOSE.is_file():
        payload = {
            "status": "FAIL",
            "summary": "compose.yaml 없음",
            "findings": ["compose.yaml:missing"],
            "file": "compose.yaml",
            "function": "services",
            "line_needle": "services:",
        }
        json.dump(payload, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0
    text = COMPOSE.read_text(encoding="utf-8")
    services = parse_services(text)
    for name in REQUIRED:
        if name not in services:
            findings.append(f"missing-service:{name}")
            continue
        meta = services[name]
        if name == "db":
            if not meta["image"]:
                findings.append("db:missing-image")
            if not meta["healthcheck"]:
                findings.append("db:missing-healthcheck")
        else:
            if not meta["build"] and not meta["image"]:
                findings.append(f"{name}:missing-build-or-image")
            if name in {"ai", "back"} and not meta["depends_on"]:
                findings.append(f"{name}:missing-depends_on")
    status = "FAIL" if findings else "PASS"
    payload = {
        "status": status,
        "summary": f"services={sorted(services)} findings={len(findings)}",
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
