#!/usr/bin/env python3
"""Second tool for the report writer. Does not use pytest."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from qa.gate import evaluate  # noqa: E402
from qa.record import COLUMNS, append_md, append_results  # noqa: E402


def row(status: str, tool: str, tc_id: str = "QA-SELF-001") -> dict:
    return {
        "RUN_ID": "R20261102-000000-test",
        "TC_ID": tc_id,
        "FEATURE_ID": "FEAT-SELF",
        "REQUIREMENT_ID": "REQ-SELF",
        "started_at": "2026-11-02T00:00:00+09:00",
        "ended_at": "2026-11-02T00:00:01+09:00",
        "area": "01_unit_integration",
        "section": "qa_recorder",
        "feature": "qa_recorder",
        "test_type": "unit",
        "tool_a": "self",
        "command_a": "self",
        "tool_a_result": tool,
        "tool_b": "self",
        "command_b": "self",
        "tool_b_result": tool,
        "final_status": status,
        "expected_result": "ok",
        "actual_result": "ok",
        "git_commit": "test",
        "file": "qa/record.py",
        "function": "append_results",
        "line": "1",
        "evidence_path": "tmp",
        "issue_id": "",
        "risk_id": "",
        "note": "selfcheck",
    }


def main() -> int:
    failures: list[str] = []
    directory = Path(tempfile.mkdtemp(prefix="qa-selfcheck-"))
    try:
        append_results(directory, [row("PASS", "PASS")])
        append_results(directory, [row("NOT_RUN", "NOT_RUN", "QA-SELF-002")])
        text = (directory / "results.tsv").read_text(encoding="utf-8-sig")
        if text.count("RUN_ID") != 1:
            failures.append("header overwritten")
        if "QA-SELF-001" not in text or "QA-SELF-002" not in text:
            failures.append("history dropped")
        if not (directory / "results.tsv").read_bytes().startswith(b"\xef\xbb\xbf"):
            failures.append("missing utf-8 bom")
        try:
            append_results(directory, [row("PASS", "NOT_RUN", "QA-SELF-003")])
            failures.append("PASS accepted a tool that was NOT_RUN")
        except ValueError:
            pass
        append_md(
            directory,
            "risk.md",
            "RISK",
            "selfcheck",
            [
                "\n".join(
                    [
                        "## R20261102-000000-test RISK-SELF-001",
                        "",
                        "- RISK_ID: RISK-SELF-001",
                        "- 심각도: HIGH",
                        "- 처리상태: OPEN",
                    ]
                )
            ],
        )
        results = directory / "results"
        target = results / "03_security_quality" / "nonfunctional_qa" / "2026-11-02"
        target.mkdir(parents=True)
        shutil.copy(directory / "risk.md", target / "risk.md")
        (target / "results.tsv").write_text("TC_ID\tfinal_status\n", encoding="utf-8")
        gate = evaluate(results, [])
        if gate.ok or not any("RISK-SELF-001" in reason for reason in gate.reasons):
            failures.append(f"gate missed HIGH risk: {gate.reasons}")
        if COLUMNS[0] != "RUN_ID" or "final_status" not in COLUMNS:
            failures.append("column contract changed")
    finally:
        shutil.rmtree(directory, ignore_errors=True)

    payload = {
        "status": "FAIL" if failures else "PASS",
        "summary": ", ".join(failures) if failures else "append, BOM, PASS rule, and HIGH gate held",
        "findings": failures,
        "file": "qa/record.py",
        "function": "append_results",
        "line_needle": "def append_results",
    }
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001
        json.dump({"status": "ERROR", "summary": str(error), "findings": []}, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        raise SystemExit(1)
