from pathlib import Path

from qa.gate import evaluate
from qa.record import append_results
from qa.run_qa import ToolOutput, decide
from qa.tests.test_record import sample


def write_risk(directory: Path, state: str, severity: str = "HIGH", risk_id: str = "RISK-SEC-001") -> None:
    directory.mkdir(parents=True, exist_ok=True)
    block = "\n".join([
        f"## R20261102-120000-abcd {risk_id}",
        "",
        f"- RISK_ID: {risk_id}",
        f"- 심각도: {severity}",
        f"- 처리상태: {state}",
    ])
    existing = directory / "risk.md"
    if existing.exists():
        existing.write_text(existing.read_text(encoding="utf-8") + "\n" + block + "\n", encoding="utf-8")
    else:
        existing.write_text("# RISK\n\n" + block + "\n", encoding="utf-8")


def test_missing_required_check_fails(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    result = evaluate(reports, ["QA-UNIT-DATA-001"])
    assert not result.ok
    assert any("QA-UNIT-DATA-001" in reason for reason in result.reasons)


def test_open_high_blocks_and_closed_does_not(tmp_path: Path) -> None:
    day = tmp_path / "reports" / "security" / "2026-11-02"
    append_results(day, [sample()])
    write_risk(day, "OPEN")
    blocked = evaluate(tmp_path / "reports", ["QA-UNIT-RECORD-001"])
    assert not blocked.ok
    assert any("RISK-SEC-001" in reason for reason in blocked.reasons)
    write_risk(day, "CLOSED")
    opened = evaluate(tmp_path / "reports", ["QA-UNIT-RECORD-001"])
    assert opened.ok


def test_medium_open_does_not_block(tmp_path: Path) -> None:
    day = tmp_path / "reports" / "unit" / "2026-11-02"
    append_results(day, [sample()])
    write_risk(day, "OPEN", "MEDIUM", "RISK-QA-001")
    result = evaluate(tmp_path / "reports", ["QA-UNIT-RECORD-001"])
    assert result.ok


def test_decide_requires_agreement() -> None:
    assert decide("pytest-json", ToolOutput("PASS", ""), ToolOutput("PASS", ""))[0] == "PASS"
    assert decide("secret", ToolOutput("PASS", "", []), ToolOutput("FAIL", "", ["a.py:1"]))[0] == "FAIL"
    same = ["back/A.java:3", "ai/src/api/main.py:8"]
    assert decide("auth", ToolOutput("PASS", "", list(reversed(same))), ToolOutput("PASS", "", same))[0] == "PASS"
    assert decide("pytest-json", ToolOutput("ERROR", ""), ToolOutput("PASS", ""))[0] == "ERROR"
