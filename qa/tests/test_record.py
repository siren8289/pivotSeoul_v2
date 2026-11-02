import csv
from pathlib import Path

import pytest

from qa.record import COLUMNS, append_md, append_results


def sample(status: str = "PASS", tool: str = "PASS", tc_id: str = "QA-UNIT-RECORD-001") -> dict:
    return {
        "RUN_ID": "R20261102-120000-abcd",
        "TC_ID": tc_id,
        "실행시각": "2026-11-02T12:00:00+09:00",
        "기능명": "qa-recorder",
        "테스트종류": "unit",
        "도구A": "pytest",
        "도구A결과": tool,
        "도구B": "record-selfcheck",
        "도구B결과": tool,
        "최종상태": status,
        "GitCommit": "abc1234",
        "파일": "qa/record.py",
        "함수": "append_results",
        "줄번호": "34",
        "ISSUE_ID": "",
        "RISK_ID": "",
        "비고": "한글, 쉼표",
    }


def test_append_keeps_earlier_rows(tmp_path: Path) -> None:
    append_results(tmp_path, [sample()])
    append_results(tmp_path, [sample("NOT_RUN", "NOT_RUN", "QA-UNIT-FRONT-001")])
    raw = (tmp_path / "results.tsv").read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    assert text.count("RUN_ID") == 1
    with (tmp_path / "results.tsv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert [row["TC_ID"] for row in rows] == ["QA-UNIT-RECORD-001", "QA-UNIT-FRONT-001"]
    assert rows[0]["비고"] == "한글, 쉼표"
    assert rows[0].keys() == set(COLUMNS) or list(rows[0]) == COLUMNS


def test_pass_rejects_unrun_tool(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="PASS"):
        append_results(tmp_path, [sample("PASS", "NOT_RUN")])


def test_markdown_appends_sections(tmp_path: Path) -> None:
    append_md(tmp_path, "pass.md", "PASS", "intro", ["## R1 QA-1\n\n- TC_ID: QA-1"])
    append_md(tmp_path, "pass.md", "PASS", "intro", ["## R2 QA-1\n\n- TC_ID: QA-1"])
    text = (tmp_path / "pass.md").read_text(encoding="utf-8")
    assert text.startswith("# PASS\n")
    assert text.count("# PASS") == 1
    assert "R1" in text and "R2" in text
