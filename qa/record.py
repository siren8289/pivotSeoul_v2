"""Append-only QA reports. Existing rows and sections are not rewritten."""

from __future__ import annotations

import csv
from pathlib import Path

STATUSES = {"PASS", "FAIL", "BLOCKED", "ERROR", "NOT_RUN", "SKIPPED"}

COLUMNS = [
    "RUN_ID",
    "TC_ID",
    "실행시각",
    "기능명",
    "테스트종류",
    "도구A",
    "도구A결과",
    "도구B",
    "도구B결과",
    "최종상태",
    "GitCommit",
    "파일",
    "함수",
    "줄번호",
    "ISSUE_ID",
    "RISK_ID",
    "비고",
]


def validate_row(row: dict) -> None:
    missing = [name for name in COLUMNS if name not in row]
    if missing:
        raise ValueError(f"missing columns: {', '.join(missing)}")
    status = row["최종상태"]
    if status not in STATUSES:
        raise ValueError(f"invalid final status: {status}")
    for key in ("도구A결과", "도구B결과"):
        if row[key] not in STATUSES:
            raise ValueError(f"invalid tool status: {row[key]}")
    if status == "PASS" and (row["도구A결과"] != "PASS" or row["도구B결과"] != "PASS"):
        raise ValueError("PASS requires both tools PASS")


def append_results(directory: Path, rows: list[dict]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "results.tsv"
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as handle:
            header = next(csv.reader(handle, delimiter="\t"), None)
        if header != COLUMNS:
            raise ValueError(f"results.tsv header mismatch: {path}")
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
