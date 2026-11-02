#!/usr/bin/env python3
"""Execute catalog TCs from qa/input/testcases.tsv with dual-tool honesty.

- Runs automated suites from test_map (required/regression).
- Writes every catalog TC into qa/results/{area}/{section}/{date}/.
- Atomic sheet TCs without dedicated commands are NOT_RUN (never fake PASS).
- Related suite results are referenced in note/risk for coverage context.
"""

from __future__ import annotations

import argparse
import csv
import secrets
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# csv used in write_day header checks

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from qa.record import COLUMNS, append_history, append_md, append_results, ensure_day_stubs  # noqa: E402
from qa.run_qa import checks_for, build_outcomes, git_commit, required_ids, write_master_xlsx  # noqa: E402
from qa.sheet import write_xlsx  # noqa: E402
from qa.gate import evaluate  # noqa: E402

QA = ROOT / "qa"
RESULTS = QA / "results"
INPUT = QA / "input" / "testcases.tsv"
HISTORY = QA / "history" / "execution_log.tsv"
SEOUL = ZoneInfo("Asia/Seoul")

# Section -> covering automated suite TC ids (context only; does not imply atomic PASS)
SECTION_SUITES = {
    "data_transform": ["QA-UNIT-DATA-001"],
    "qa_recorder": ["QA-UNIT-RECORD-001"],
    "db_persist": ["QA-INT-PIPELINE-001"],
    "common_ui": ["QA-UNIT-FRONT-001"],
    "diagnosis_api": ["QA-API-CONTRACT-001"],
    "diagnosis_input": ["QA-E2E-FLOW-001"],
    "nonfunctional_qa": ["QA-SEC-SECRET-001", "QA-SEC-AUTH-001", "QA-SEC-SEMGREP-001", "QA-PERF-BENCH-001"],
    "deploy_ci": ["QA-INFRA-COMPOSE-001"],
    "deployment": ["QA-INFRA-SMOKE-001"],
}


def load_catalog() -> list[dict]:
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_day(directory: Path, rows: list[dict], passes: list[str], fails: list[str], risks: list[str]) -> None:
    ensure_day_stubs(directory)
    results_path = directory / "results.tsv"
    if results_path.exists():
        with results_path.open(encoding="utf-8-sig", newline="") as handle:
            header = next(csv.reader(handle, delimiter="\t"), None)
        if header != COLUMNS:
            results_path.rename(directory / f"results_legacy_{secrets.token_hex(2)}.tsv")
            ensure_day_stubs(directory)
    if rows:
        append_results(directory, rows)
    append_md(directory, "pass.md", "PASS", "통과한 TC.", passes)
    append_md(directory, "fail.md", "FAIL", "실패·오류.", fails)
    append_md(directory, "risk.md", "RISK", "위험 등록부.", risks)
    sheet_rows: list[list[object]] = [list(COLUMNS)]
    with (directory / "results.tsv").open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            sheet_rows.append([row.get(name, "") for name in COLUMNS])
    write_xlsx(directory / "test_sheet.xlsx", {"Results": sheet_rows})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("required", "regression"), default="regression")
    parser.add_argument("--area", default=None)
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--skip-suites", action="store_true", help="catalog only; do not rerun suites")
    args = parser.parse_args(argv)

    if not INPUT.exists():
        raise SystemExit("missing qa/input/testcases.tsv — run qa/tools/import_qa_sheet.py first")

    catalog = load_catalog()
    if args.area:
        catalog = [row for row in catalog if row.get("area") == args.area]
    if not catalog:
        raise SystemExit("no catalog rows")

    now = datetime.now(SEOUL)
    run_id = f"R{now:%Y%m%d-%H%M%S}-{secrets.token_hex(2)}"
    day = now.strftime("%Y-%m-%d")
    when = now.strftime("%Y-%m-%dT%H:%M:%S+09:00")
    commit = git_commit()

    suite_status: dict[str, str] = {}
    suite_note: dict[str, str] = {}
    if not args.skip_suites:
        suites = checks_for(args.profile)
        if args.area:
            suites = [item for item in suites if item.area == args.area]
        outcomes = build_outcomes(suites)
        # persist suite outcomes via existing day writer logic (minimal)
        by_section: dict[tuple[str, str], list] = defaultdict(list)
        for item in outcomes:
            suite_status[item.check.tc_id] = item.final
            suite_note[item.check.tc_id] = item.note
            evidence = str((RESULTS / item.check.area / item.check.section / day).relative_to(ROOT))
            row = {
                "RUN_ID": run_id,
                "TC_ID": item.check.tc_id,
                "FEATURE_ID": item.check.feature_id,
                "REQUIREMENT_ID": item.check.requirement_id,
                "started_at": item.started_at,
                "ended_at": item.ended_at,
                "area": item.check.area,
                "section": item.check.section,
                "feature": item.check.feature,
                "test_type": item.check.test_type,
                "tool_a": item.check.tool_a,
                "command_a": " ".join(item.check.cmd_a),
                "tool_a_result": item.tool_a.status,
                "tool_b": item.check.tool_b,
                "command_b": " ".join(item.check.cmd_b),
                "tool_b_result": item.tool_b.status,
                "final_status": item.final,
                "expected_result": item.check.expected_result,
                "actual_result": item.note,
                "git_commit": commit,
                "file": item.check.file,
                "function": item.check.function,
                "line": item.line,
                "evidence_path": evidence,
                "issue_id": "",
                "risk_id": item.risk_id,
                "note": item.note,
            }
            by_section[(item.check.area, item.check.section)].append((row, item))
        for (area, section), entries in by_section.items():
            directory = RESULTS / area / section / day
            rows = [e[0] for e in entries]
            passes: list[str] = []
            fails: list[str] = []
            risks: list[str] = []
            for row, item in entries:
                heading = f"## {run_id} {item.check.tc_id}"
                body = [
                    heading,
                    "",
                    f"- TC_ID: {item.check.tc_id}",
                    f"- 최종상태: {item.final}",
                    f"- 도구A: {item.tool_a.status}",
                    f"- 도구B: {item.tool_b.status}",
                    f"- 실제결과: {item.note}",
                ]
                if item.final == "PASS":
                    passes.append("\n".join(body))
                else:
                    fails.append("\n".join(body))
                if item.risk_md:
                    risks.append(item.risk_md.replace("{run_id}", run_id).replace("{when}", when))
            write_day(directory, rows, passes, fails, risks)
            append_history(HISTORY, rows)
            for row, item in entries:
                print(f"SUITE {row['TC_ID']} {row['final_status']} {area}/{section}")

    # Catalog atomic TCs
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    counts = defaultdict(int)
    for tc in catalog:
        area = tc.get("area") or "UNKNOWN"
        section = tc.get("section") or "unknown"
        if area == "UNKNOWN":
            continue
        suites = SECTION_SUITES.get(section, [])
        related = ", ".join(f"{sid}={suite_status.get(sid, 'NOT_RUN')}" for sid in suites) if suites else "none"
        note = (
            f"원자 TC 전용 이중 명령 미연결. 실행하지 않아 PASS 처리하지 않음. "
            f"관련 스위트: {related}. scenario={tc.get('scenario','')[:80]}"
        )
        row = {
            "RUN_ID": run_id,
            "TC_ID": tc["tc_id"],
            "FEATURE_ID": tc.get("feature_id", ""),
            "REQUIREMENT_ID": tc.get("requirement_id", ""),
            "started_at": when,
            "ended_at": when,
            "area": area,
            "section": section,
            "feature": tc.get("legacy_area", ""),
            "test_type": tc.get("type", ""),
            "tool_a": "NOT_MAPPED",
            "command_a": "",
            "tool_a_result": "NOT_RUN",
            "tool_b": "NOT_MAPPED",
            "command_b": "",
            "tool_b_result": "NOT_RUN",
            "final_status": "NOT_RUN",
            "expected_result": tc.get("expected", ""),
            "actual_result": "미실행(자동화 매핑 없음)",
            "git_commit": commit,
            "file": (tc.get("target_source") or "UNKNOWN").split(";")[0].strip() or "UNKNOWN",
            "function": "UNKNOWN",
            "line": "UNKNOWN",
            "evidence_path": f"qa/results/{area}/{section}/{day}",
            "issue_id": "",
            "risk_id": "RISK-SHEET-NOT-MAPPED",
            "note": note,
        }
        grouped[(area, section)].append(row)
        counts["NOT_RUN"] += 1

    risk_block = "\n".join(
        [
            f"## {run_id} RISK-SHEET-NOT-MAPPED",
            "",
            "- RISK_ID: RISK-SHEET-NOT-MAPPED",
            "- TC_ID: SHEET-CATALOG",
            f"- 실행시각: {when}",
            "- 심각도: MEDIUM",
            "- 발생가능성: HIGH",
            "- 영향: 749 원자 TC 중 전용 이중 검증 명령이 없는 항목은 NOT_RUN이다. 관련 스위트 PASS를 개별 TC PASS로 대체하지 않는다.",
            "- 처리상태: OPEN",
            "- 권장조치: 우선순위 P0부터 test_map.json에 TOOL_A/B 명령을 연결한다.",
            "- 파일: qa/input/testcases.tsv",
            "- 함수: UNKNOWN",
            "- 줄번호: UNKNOWN",
            "- ISSUE_ID: ",
            "- 근거: V3 정책 — 미실행 PASS 금지",
        ]
    )

    for (area, section), rows in grouped.items():
        directory = RESULTS / area / section / day
        write_day(directory, rows, [], [], [risk_block] if rows else [])
        append_history(HISTORY, rows)
        print(f"CATALOG {area}/{section} NOT_RUN={len(rows)}")

    write_master_xlsx([])
    print(f"RUN_ID {run_id}")
    print(f"SUMMARY catalog_not_run={counts['NOT_RUN']} suites={suite_status}")

    if args.gate:
        result = evaluate(RESULTS, required_ids())
        if result.ok:
            print("GATE PASS")
            return 0
        print("GATE FAIL")
        for reason in result.reasons:
            print(f"- {reason}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
