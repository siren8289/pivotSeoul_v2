import csv
from pathlib import Path

import pytest

from qa.record import COLUMNS, append_md, append_results


def sample(status: str = "PASS", tool: str = "PASS", tc_id: str = "QA-UNIT-RECORD-001") -> dict:
    return {
        "RUN_ID": "R20261102-120000-abcd",
        "TC_ID": tc_id,
        "FEATURE_ID": "FEAT-QA-RECORD",
        "REQUIREMENT_ID": "REQ-QA-V3",
        "started_at": "2026-11-02T12:00:00+09:00",
        "ended_at": "2026-11-02T12:00:01+09:00",
        "area": "01_unit_integration",
        "section": "qa_recorder",
        "feature": "qa_recorder",
        "test_type": "unit",
        "tool_a": "pytest",
        "command_a": "pytest",
        "tool_a_result": tool,
        "tool_b": "record-selfcheck",
        "command_b": "record_selfcheck",
        "tool_b_result": tool,
        "final_status": status,
        "expected_result": "누적 기록",
        "actual_result": "ok",
        "git_commit": "abc1234",
        "file": "qa/record.py",
        "function": "append_results",
        "line": "34",
        "evidence_path": "qa/results/01_unit_integration/qa_recorder/2026-11-02",
        "issue_id": "",
        "risk_id": "",
        "note": "한글, 쉼표",
    }


def test_append_keeps_earlier_rows(tmp_path: Path) -> None:
    append_results(tmp_path, [sample()])
    append_results(tmp_path, [sample("NOT_RUN", "NOT_RUN", "QA-UNIT-FRONT-001")])
    raw = (tmp_path / "results.tsv").read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    with (tmp_path / "results.tsv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert [row["TC_ID"] for row in rows] == ["QA-UNIT-RECORD-001", "QA-UNIT-FRONT-001"]
    assert rows[0]["note"] == "한글, 쉼표"
    assert list(rows[0].keys()) == COLUMNS


def test_pass_rejects_unrun_tool(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="PASS"):
        append_results(tmp_path, [sample("PASS", "NOT_RUN")])


def test_markdown_appends_sections(tmp_path: Path) -> None:
    append_md(tmp_path, "pass.md", "PASS", "intro", ["## R1 QA-1\n\n- TC_ID: QA-1"])
    append_md(tmp_path, "pass.md", "PASS", "intro", ["## R2 QA-1\n\n- TC_ID: QA-1"])
    text = (tmp_path / "pass.md").read_text(encoding="utf-8")
    assert text.startswith("# PASS\n")
    assert "R1" in text and "R2" in text
