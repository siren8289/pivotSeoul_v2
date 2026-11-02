#!/usr/bin/env python3
"""Import pivotSeoul QA Excel (전체_TC) into qa/input/testcases.tsv."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / "qa"
INPUT = QA / "input" / "testcases.tsv"

SECTION_MAP = {
    "PS-DT": ("01_unit_integration", "data_transform"),
    "PS-DP": ("01_unit_integration", "etl_pipeline"),
    "PS-DF": ("01_unit_integration", "public_api_ingest"),
    "PS-DB": ("01_unit_integration", "db_persist"),
    "PS-ML": ("01_unit_integration", "ml_price_predict"),
    "PS-RIR": ("01_unit_integration", "rir_rules"),
    "PS-LLM": ("01_unit_integration", "llm_explain"),
    "PS-BD": ("02_web_api", "diagnosis_api"),
    "PS-BR": ("02_web_api", "recommendation_api"),
    "PS-BE": ("02_web_api", "integration_errors"),
    "PS-RE": ("02_web_api", "rag_eligibility"),
    "PS-RG": ("02_web_api", "rag_guidance"),
    "PS-RS": ("02_web_api", "rag_search"),
    "PS-UI": ("02_web_api", "common_ui"),
    "PS-FD": ("02_web_api", "diagnosis_input"),
    "PS-FC": ("02_web_api", "district_recommend_ui"),
    "PS-FR": ("02_web_api", "diagnosis_result"),
    "PS-Q": ("03_security_quality", "nonfunctional_qa"),
    "PS-RH": ("03_security_quality", "rag_security"),
    "PS-OPS": ("04_infra_deploy", "deploy_ci"),
}

HEADERS = [
    "area",
    "section",
    "tc_id",
    "feature_id",
    "requirement_id",
    "legacy_area",
    "major",
    "minor",
    "type",
    "priority",
    "scenario",
    "precondition",
    "input",
    "steps",
    "expected",
    "criteria",
    "status",
    "actual",
    "defect_id",
    "automation",
    "basis",
    "target_source",
    "ref_url",
    "note",
]


def find_sheet() -> Path:
    for path in QA.iterdir():
        if path.suffix.lower() == ".xlsx" and path.name != "master_test_sheet.xlsx":
            return path
    raise SystemExit("QA Excel sheet not found under qa/")


def prefix_of(tc_id: str) -> str:
    matched = re.match(r"(PS-[A-Z]+)", tc_id or "")
    return matched.group(1) if matched else ""


def load_rows(path: Path) -> list[dict]:
    import openpyxl

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    if "전체_TC" not in wb.sheetnames:
        raise SystemExit("sheet 전체_TC missing")
    rows = list(wb["전체_TC"].iter_rows(values_only=True))
    hdr_i = next(i for i, row in enumerate(rows[:10]) if row and row[0] == "TC ID")
    header = [str(h) if h else f"c{i}" for i, h in enumerate(rows[hdr_i])]
    out: list[dict] = []
    for raw in rows[hdr_i + 1 :]:
        if not raw or not raw[0]:
            continue
        tc_id = str(raw[0]).strip()
        if not tc_id.startswith(("PS-", "QA-")):
            continue
        src = dict(zip(header, raw))
        prefix = prefix_of(tc_id)
        area, section = SECTION_MAP.get(prefix, ("UNKNOWN", "unknown"))
        status = str(src.get("실행 상태") or "NOT_RUN")
        if status in {"미실행", ""}:
            status = "NOT_RUN"
        out.append(
            {
                "area": area,
                "section": section,
                "tc_id": tc_id,
                "feature_id": f"FEAT-{prefix}" if prefix else "",
                "requirement_id": f"REQ-{prefix}" if prefix else "",
                "legacy_area": str(src.get("분야") or ""),
                "major": str(src.get("중분류") or ""),
                "minor": str(src.get("세부기능") or ""),
                "type": str(src.get("테스트유형") or ""),
                "priority": str(src.get("우선순위") or ""),
                "scenario": str(src.get("테스트 시나리오") or ""),
                "precondition": str(src.get("사전조건") or ""),
                "input": str(src.get("입력·테스트데이터") or ""),
                "steps": str(src.get("실행 절차") or ""),
                "expected": str(src.get("기대 결과") or ""),
                "criteria": str(src.get("판정 기준") or ""),
                "status": status,
                "actual": str(src.get("실제 결과") or ""),
                "defect_id": str(src.get("결함 ID") or ""),
                "automation": str(src.get("자동화") or ""),
                "basis": str(src.get("근거 구분") or ""),
                "target_source": str(src.get("관련 코드 경로") or ""),
                "ref_url": str(src.get("GitHub 소스 링크") or ""),
                "note": str(src.get("비고/확인사항") or ""),
            }
        )
    return out


def main() -> int:
    sheet = find_sheet()
    rows = load_rows(sheet)
    INPUT.parent.mkdir(parents=True, exist_ok=True)
    with INPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADERS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"imported {len(rows)} TCs from {sheet.name} -> {INPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
