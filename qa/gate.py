"""Decide whether required checks and blocking risks allow completion."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

BLOCKING_SEVERITY = {"HIGH", "CRITICAL"}
AREA_DIRS = (
    "01_unit_integration",
    "02_web_api",
    "03_security_quality",
    "04_infra_deploy",
)


@dataclass
class GateResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)


def _area_roots(results_root: Path) -> list[Path]:
    if not results_root.exists():
        return []
    return [results_root / name for name in AREA_DIRS if (results_root / name).is_dir()]


def _risk_sections(results_root: Path) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    files: list[Path] = []
    for root in _area_roots(results_root):
        files.extend(sorted(root.glob("*/*/risk.md")))
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


def latest_risks(results_root: Path) -> dict[str, dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    for section in _risk_sections(results_root):
        risk_id = section.get("RISK_ID", "").strip()
        if risk_id:
            latest[risk_id] = section
    return latest


def latest_results(results_root: Path) -> dict[str, dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    files: list[Path] = []
    for root in _area_roots(results_root):
        files.extend(sorted(root.glob("*/*/summary.tsv")))
    for path in files:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                tc_id = (row.get("TC_ID") or "").strip()
                if tc_id:
                    latest[tc_id] = row
    return latest


def evaluate(results_root: Path, required_ids: list[str]) -> GateResult:
    reasons: list[str] = []
    results = latest_results(results_root)
    for tc_id in required_ids:
        row = results.get(tc_id)
        if row is None:
            reasons.append(f"{tc_id} 기록이 없습니다.")
            continue
        status = row.get("final_status", "")
        if status != "PASS":
            reasons.append(f"{tc_id} 최종상태가 {status or 'UNKNOWN'} 입니다.")
    for risk_id, section in latest_risks(results_root).items():
        severity = section.get("심각도", "")
        state = section.get("처리상태", "")
        if severity in BLOCKING_SEVERITY and state == "OPEN":
            reasons.append(f"{risk_id} {severity} OPEN")
    return GateResult(ok=not reasons, reasons=reasons)
