from pathlib import Path

from qa.gate import evaluate
from qa.record import append_results
from qa.run_qa import ToolOutput, decide
from qa.tests.test_record import sample


def write_risk(directory: Path, state: str, severity: str = "HIGH", risk_id: str = "RISK-SEC-001") -> None:
    directory.mkdir(parents=True, exist_ok=True)
    block = "\n".join(
        [
            f"## R20261102-120000-abcd {risk_id}",
            "",
            f"- RISK_ID: {risk_id}",
            f"- 심각도: {severity}",
            f"- 처리상태: {state}",
        ]
    )
    existing = directory / "risk.md"
    if existing.exists():
        existing.write_text(existing.read_text(encoding="utf-8") + "\n" + block + "\n", encoding="utf-8")
    else:
        existing.write_text("# RISK\n\n" + block + "\n", encoding="utf-8")


def test_missing_required_check_fails(tmp_path: Path) -> None:
    result = evaluate(tmp_path / "results", ["QA-UNIT-DATA-001"])
    assert not result.ok


def test_open_high_blocks_and_closed_does_not(tmp_path: Path) -> None:
    day = tmp_path / "results" / "03_security_quality" / "nonfunctional_qa" / "2026-11-02"
    append_results(day, [sample()])
    write_risk(day, "OPEN")
    blocked = evaluate(tmp_path / "results", ["QA-UNIT-RECORD-001"])
    assert not blocked.ok
    write_risk(day, "CLOSED")
    assert evaluate(tmp_path / "results", ["QA-UNIT-RECORD-001"]).ok


def test_medium_open_does_not_block(tmp_path: Path) -> None:
    day = tmp_path / "results" / "01_unit_integration" / "qa_recorder" / "2026-11-02"
    append_results(day, [sample()])
    write_risk(day, "OPEN", "MEDIUM", "RISK-QA-001")
    assert evaluate(tmp_path / "results", ["QA-UNIT-RECORD-001"]).ok


def test_decide_requires_agreement() -> None:
    assert decide("pytest-json", ToolOutput("PASS", ""), ToolOutput("PASS", ""))[0] == "PASS"
    assert decide("json-pair", ToolOutput("BLOCKED", ""), ToolOutput("PASS", ""))[0] == "BLOCKED"
    assert decide("secret", ToolOutput("PASS", "", []), ToolOutput("FAIL", "", ["a.py:1"]))[0] == "FAIL"
    same = ["back/A.java:3", "ai/src/api/main.py:8"]
    assert decide("auth", ToolOutput("PASS", "", list(reversed(same))), ToolOutput("PASS", "", same))[0] == "PASS"
