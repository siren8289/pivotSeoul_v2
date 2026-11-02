"""Decide whether required checks and blocking risks allow completion."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

BLOCKING_SEVERITY = {"HIGH", "CRITICAL"}


@dataclass
class GateResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)


def _risk_sections(reports: Path) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    if not reports.exists():
        return sections
    files = sorted(reports.glob("*/*/risk.md"))
    for path in files:
        current: dict[str, str] | None = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                if current:
                    sections.append(current)
                current = {"_file": str(path)}
                continue
            if current is None or not line.startswith("- "):
                continue
            if ": " not in line:
                continue
            key, value = line[2:].split(": ", 1)
            current[key] = value
        if current:
            sections.append(current)
    return sections


def latest_risks(reports: Path) -> dict[str, dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    for section in _risk_sections(reports):
        risk_id = section.get("RISK_ID", "").strip()
        if risk_id:
            latest[risk_id] = section
    return latest


def latest_results(reports: Path) -> dict[str, dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    if not reports.exists():
        return latest
    files = sorted(reports.glob("*/*/results.tsv"))
    for path in files:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                tc_id = (row.get("TC_ID") or "").strip()
                if tc_id:
                    latest[tc_id] = row
    return latest


def evaluate(reports: Path, required_ids: list[str]) -> GateResult:
    reasons: list[str] = []
    results = latest_results(reports)
    for tc_id in required_ids:
        row = results.get(tc_id)
        if row is None:
            reasons.append(f"{tc_id} 기록이 없습니다.")
            continue
        status = row.get("최종상태", "")
        if status != "PASS":
            reasons.append(f"{tc_id} 최종상태가 {status or 'UNKNOWN'} 입니다.")
    for risk_id, section in latest_risks(reports).items():
        severity = section.get("심각도", "")
        state = section.get("처리상태", "")
        if severity in BLOCKING_SEVERITY and state == "OPEN":
            reasons.append(f"{risk_id} {severity} OPEN")
    return GateResult(ok=not reasons, reasons=reasons)
