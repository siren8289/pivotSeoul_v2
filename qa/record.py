"""Append-only QA reports under qa/results/{area}/{section}/{date}/."""

from __future__ import annotations

import csv
import os
import tempfile
import time
from pathlib import Path

STATUSES = {"PASS", "FAIL", "BLOCKED", "ERROR", "NOT_RUN", "SKIPPED"}

COLUMNS = [
    "RUN_ID",
    "TC_ID",
    "FEATURE_ID",
    "REQUIREMENT_ID",
    "started_at",
    "ended_at",
    "area",
    "section",
    "feature",
    "test_type",
    "tool_a",
    "command_a",
    "tool_a_result",
    "tool_b",
    "command_b",
    "tool_b_result",
    "final_status",
    "expected_result",
    "actual_result",
    "git_commit",
    "file",
    "function",
    "line",
    "evidence_path",
    "issue_id",
    "risk_id",
    "note",
]

HISTORY_COLUMNS = [
    "RUN_ID",
    "TC_ID",
    "FEATURE_ID",
    "area",
    "section",
    "started_at",
    "ended_at",
    "tool_a",
    "tool_a_result",
    "tool_b",
    "tool_b_result",
    "final_status",
    "git_commit",
    "evidence_dir",
    "note",
]

DAY_FILES = ("test_sheet.xlsx", "pass.md", "fail.md", "risk.md", "results.tsv")


class FileLock:
    def __init__(self, path: Path, timeout: float = 30.0) -> None:
        self.lock_path = path.with_suffix(path.suffix + ".lock")
        self.timeout = timeout
        self._fd: int | None = None

    def __enter__(self) -> FileLock:
        start = time.time()
        while True:
            try:
                self._fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self._fd, str(os.getpid()).encode())
                return self
            except FileExistsError:
                if time.time() - start > self.timeout:
                    raise TimeoutError(f"lock timeout: {self.lock_path}")
                time.sleep(0.05)

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        try:
            self.lock_path.unlink(missing_ok=True)
        except OSError:
            pass


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


def _append_tsv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(path):
        if path.exists():
            with path.open(encoding="utf-8-sig", newline="") as handle:
                header = next(csv.reader(handle, delimiter="\t"), None)
            if header != columns:
                raise ValueError(f"header mismatch: {path}")
            mode_encoding = "utf-8"
        else:
            mode_encoding = "utf-8-sig"
        with path.open("a", encoding=mode_encoding, newline="") as handle:
            writer = csv.writer(handle, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
            if mode_encoding == "utf-8-sig":
                writer.writerow(columns)
            for row in rows:
                writer.writerow([row.get(name, "") for name in columns])


def append_results(directory: Path, rows: list[dict]) -> None:
    for row in rows:
        validate_row(row)
    _append_tsv(directory / "results.tsv", COLUMNS, rows)


append_summary = append_results


def append_history(history_path: Path, rows: list[dict]) -> None:
    payload = []
    for row in rows:
        payload.append(
            {
                "RUN_ID": row.get("RUN_ID", ""),
                "TC_ID": row.get("TC_ID", ""),
                "FEATURE_ID": row.get("FEATURE_ID", ""),
                "area": row.get("area", ""),
                "section": row.get("section", ""),
                "started_at": row.get("started_at", ""),
                "ended_at": row.get("ended_at", ""),
                "tool_a": row.get("tool_a", ""),
                "tool_a_result": row.get("tool_a_result", ""),
                "tool_b": row.get("tool_b", ""),
                "tool_b_result": row.get("tool_b_result", ""),
                "final_status": row.get("final_status", ""),
                "git_commit": row.get("git_commit", ""),
                "evidence_dir": row.get("evidence_path", ""),
                "note": row.get("note", ""),
            }
        )
    _append_tsv(history_path, HISTORY_COLUMNS, payload)


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
        ("risk.md", "RISK", "잠재 위험 등록부. 실행 상태와 별개이며 같은 RISK_ID의 마지막 처리상태가 현재 상태다."),
    ):
        path = directory / name
        if not path.exists():
            path.write_text(f"# {title}\n\n{intro}\n", encoding="utf-8")
    results = directory / "results.tsv"
    if not results.exists():
        with results.open("w", encoding="utf-8-sig", newline="") as handle:
            csv.writer(handle, delimiter="\t", lineterminator="\n").writerow(COLUMNS)


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(path):
        fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".")
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
            Path(tmp_name).replace(path)
        finally:
            try:
                Path(tmp_name).unlink(missing_ok=True)
            except OSError:
                pass
