"""Append-only QA reports under qa/results/{area}/{section}/{date}/."""

from __future__ import annotations

import csv
from pathlib import Path

STATUSES = {"PASS", "FAIL", "BLOCKED", "ERROR", "NOT_RUN", "SKIPPED", "RISK"}

COLUMNS = [
    "RUN_ID",
    "TC_ID",
    "executed_at",
    "area",
    "section",
    "feature",
    "test_type",
    "tool_a",
    "tool_a_result",
    "tool_b",
    "tool_b_result",
    "final_status",
    "git_commit",
    "file",
    "function",
    "line",
    "issue_id",
    "risk_id",
    "note",
]

DAY_FILES = ("test_sheet.xlsx", "pass.md", "fail.md", "risk.md", "summary.tsv")


def validate_row(row: dict) -> None:
    missing = [name for name in COLUMNS if name not in row]
    if missing:
        raise ValueError(f"missing columns: {', '.join(missing)}")
    status = row["final_status"]
    if status not in STATUSES:
        raise ValueError(f"invalid final status: {status}")
    for key in ("tool_a_result", "tool_b_result"):
        if row[key] not in STATUSES:
            raise ValueError(f"invalid tool status: {row[key]}")
    if status == "PASS" and (row["tool_a_result"] != "PASS" or row["tool_b_result"] != "PASS"):
        raise ValueError("PASS requires both tools PASS")


def append_summary(directory: Path, rows: list[dict]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "summary.tsv"
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as handle:
            header = next(csv.reader(handle, delimiter="\t"), None)
        if header != COLUMNS:
            raise ValueError(f"summary.tsv header mismatch: {path}")
        mode_encoding = "utf-8"
    else:
        mode_encoding = "utf-8-sig"
    with path.open("a", encoding=mode_encoding, newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        if mode_encoding == "utf-8-sig":
            writer.writerow(COLUMNS)
        for row in rows:
            validate_row(row)
            writer.writerow([row[name] for name in COLUMNS])


append_results = append_summary


def append_md(directory: Path, filename: str, title: str, intro: str, blocks: list[str]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    if not path.exists():
        path.write_text(f"# {title}\n\n{intro}\n", encoding="utf-8")
    if not blocks:
        return
    with path.open("a", encoding="utf-8") as handle:
        for block in blocks:
            handle.write("\n")
            handle.write(block.rstrip())
            handle.write("\n")


def ensure_day_stubs(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name, title, intro in (
        ("pass.md", "PASS", "통과한 TC. 이전 절은 삭제하지 않는다."),
        ("fail.md", "FAIL", "실패와 도구 오류. 해당 실행에 없으면 제목만 남는다."),
        ("risk.md", "RISK", "잠재 위험. 같은 RISK_ID의 마지막 처리상태가 현재 상태다."),
    ):
        path = directory / name
        if not path.exists():
            path.write_text(f"# {title}\n\n{intro}\n", encoding="utf-8")
    if not (directory / "summary.tsv").exists():
        with (directory / "summary.tsv").open("w", encoding="utf-8-sig", newline="") as handle:
            csv.writer(handle, delimiter="\t", lineterminator="\n").writerow(COLUMNS)
