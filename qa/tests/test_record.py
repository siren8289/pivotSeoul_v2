import csv
from pathlib import Path

import pytest

from qa.record import COLUMNS, append_md, append_summary


def sample(status: str = "PASS", tool: str = "PASS", tc_id: str = "QA-UNIT-RECORD-001") -> dict:
    return {
        "RUN_ID": "R20261102-120000-abcd",
        "TC_ID": tc_id,
        "executed_at": "2026-11-02T12:00:00+09:00",
        "area": "01_unit_integration",
        "section": "qa_recorder",
        "feature": "qa_recorder",
        "test_type": "unit",
        "tool_a": "pytest",
        "tool_a_result": tool,
        "tool_b": "record-selfcheck",
        "tool_b_result": tool,
        "final_status": status,
        "git_commit": "abc1234",
        "file": "qa/record.py",
        "function": "append_summary",
        "line": "34",
        "issue_id": "",
        "risk_id": "",
        "note": "한글, 쉼표",
    }


def test_append_keeps_earlier_rows(tmp_path: Path) -> None:
    append_summary(tmp_path, [sample()])
    append_summary(tmp_path, [sample("NOT_RUN", "NOT_RUN", "QA-UNIT-FRONT-001")])
    raw = (tmp_path / "summary.tsv").read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    assert text.count("RUN_ID") == 1
    with (tmp_path / "summary.tsv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert [row["TC_ID"] for row in rows] == ["QA-UNIT-RECORD-001", "QA-UNIT-FRONT-001"]
    assert rows[0]["note"] == "한글, 쉼표"
    assert list(rows[0].keys()) == COLUMNS


def test_pass_rejects_unrun_tool(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="PASS"):
        append_summary(tmp_path, [sample("PASS", "NOT_RUN")])


def test_markdown_appends_sections(tmp_path: Path) -> None:
    append_md(tmp_path, "pass.md", "PASS", "intro", ["## R1 QA-1\n\n- TC_ID: QA-1"])
    append_md(tmp_path, "pass.md", "PASS", "intro", ["## R2 QA-1\n\n- TC_ID: QA-1"])
    text = (tmp_path / "pass.md").read_text(encoding="utf-8")
    assert text.startswith("# PASS\n")
    assert text.count("# PASS") == 1
    assert "R1" in text and "R2" in text
