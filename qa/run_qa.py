#!/usr/bin/env python3
"""V3 QA runner: dual-tool checks from test_map.json, append-only evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
import secrets
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from qa.gate import evaluate  # noqa: E402
from qa.record import (  # noqa: E402
    COLUMNS,
    append_history,
    append_md,
    append_results,
    ensure_day_stubs,
)
from qa.sheet import write_xlsx  # noqa: E402

QA_ROOT = ROOT / "qa"
RESULTS = QA_ROOT / "results"
HISTORY = QA_ROOT / "history" / "execution_log.tsv"
TEST_MAP = QA_ROOT / "config" / "test_map.json"
MASTER_XLSX = QA_ROOT / "master_test_sheet.xlsx"
INPUT_TC = QA_ROOT / "input" / "testcases.tsv"
SEOUL = ZoneInfo("Asia/Seoul")
AREAS = (
    "01_unit_integration",
    "02_web_api",
    "03_security_quality",
    "04_infra_deploy",
)


@dataclass
class Check:
    tc_id: str
    area: str
    section: str
    feature: str
    feature_id: str
    requirement_id: str
    test_type: str
    tool_a: str
    cmd_a: list[str]
    tool_b: str
    cmd_b: list[str]
    kind: str
    file: str
    function: str
    line_needle: str
    scope: str
    expected_result: str
    required: bool


@dataclass
class ToolOutput:
    status: str
    summary: str
    findings: list[str] = field(default_factory=list)
    file: str = ""
    function: str = ""
    line_needle: str = ""
    detail: str = ""


@dataclass
class Outcome:
    check: Check
    tool_a: ToolOutput
    tool_b: ToolOutput
    final: str
    note: str
    line: str
    started_at: str
    ended_at: str
    risk_md: str = ""
    risk_id: str = ""


def load_map() -> dict:
    return json.loads(TEST_MAP.read_text(encoding="utf-8"))


def expand_cmd(parts: list[str]) -> list[str]:
    python = sys.executable
    return [python if part == "{python}" else part for part in parts]


def checks_for(profile: str) -> list[Check]:
    data = load_map()
    required_ids = list(data["required_ids"])
    if profile == "regression":
        required_ids = required_ids + list(data.get("regression_extra_ids", []))
    elif profile != "required":
        raise SystemExit(f"unknown profile: {profile}")

    items: list[Check] = []
    for tc_id in required_ids:
        raw = data["checks"][tc_id]
        items.append(
            Check(
                tc_id=tc_id,
                area=raw["area"],
                section=raw["section"],
                feature=raw["feature"],
                feature_id=raw.get("feature_id", ""),
                requirement_id=raw.get("requirement_id", ""),
                test_type="regression" if profile == "regression" else raw["test_type"],
                tool_a=raw["tool_a"],
                cmd_a=expand_cmd(raw["command_a"]),
                tool_b=raw["tool_b"],
                cmd_b=expand_cmd(raw["command_b"]),
                kind=raw["kind"],
                file=raw["file"],
                function=raw["function"],
                line_needle=raw["line_needle"],
                scope=raw.get("scope", ""),
                expected_result=raw.get("expected_result", ""),
                required=raw.get("required", tc_id in data["required_ids"]),
            )
        )
    return items


def required_ids() -> list[str]:
    return list(load_map()["required_ids"])


def line_of(relative: str, needle: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        return "UNKNOWN"
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if needle in line:
            return str(number)
    return "UNKNOWN"


def git_commit() -> str:
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "UNKNOWN"
    status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True)
    if status.stdout.strip():
        return f"{sha}+dirty"
    return sha or "UNKNOWN"


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=300, check=False)


def tail(text: str, limit: int = 1200) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else compact[:limit] + "…"


def parse_json_tool(completed: subprocess.CompletedProcess[str]) -> ToolOutput:
    detail = tail(completed.stdout + "\n" + completed.stderr)
    if completed.returncode != 0 and not completed.stdout.strip():
        return ToolOutput("ERROR", f"exit {completed.returncode}", detail=detail)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return ToolOutput("ERROR", "JSON이 아닙니다.", detail=detail)
    status = payload.get("status", "ERROR")
    if status not in {"PASS", "FAIL", "ERROR", "BLOCKED", "NOT_RUN", "SKIPPED"}:
        return ToolOutput("ERROR", f"도구 상태 {status}", detail=detail)
    return ToolOutput(
        status=status,
        summary=str(payload.get("summary", "")),
        findings=[str(item) for item in payload.get("findings", [])],
        file=str(payload.get("file", "")),
        function=str(payload.get("function", "")),
        line_needle=str(payload.get("line_needle", "")),
        detail=detail,
    )


def parse_pytest(completed: subprocess.CompletedProcess[str]) -> ToolOutput:
    detail = tail(completed.stdout + "\n" + completed.stderr)
    if completed.returncode == 0:
        return ToolOutput("PASS", "pytest exit 0", detail=detail)
    if completed.returncode == 1:
        return ToolOutput("FAIL", "pytest exit 1", detail=detail)
    return ToolOutput("ERROR", f"pytest exit {completed.returncode}", detail=detail)


def parse_node_test(completed: subprocess.CompletedProcess[str]) -> ToolOutput:
    detail = tail(completed.stdout + "\n" + completed.stderr)
    if completed.returncode == 0:
        return ToolOutput("PASS", "node --test exit 0", detail=detail)
    if completed.returncode == 1:
        return ToolOutput("FAIL", "node --test exit 1", detail=detail)
    return ToolOutput("ERROR", f"node --test exit {completed.returncode}", detail=detail)


def execute(check: Check) -> tuple[ToolOutput, ToolOutput]:
    first = run_command(check.cmd_a)
    second = run_command(check.cmd_b)
    if check.kind == "pytest-json":
        return parse_pytest(first), parse_json_tool(second)
    if check.kind == "node-json":
        return parse_node_test(first), parse_json_tool(second)
    return parse_json_tool(first), parse_json_tool(second)


def decide(kind: str, first: ToolOutput, second: ToolOutput) -> tuple[str, str]:
    for status in (first.status, second.status):
        if status == "ERROR":
            return "ERROR", "도구 실행 오류"
        if status == "BLOCKED":
            return "BLOCKED", "선행 환경/도구 부재로 검증 불가"
        if status in {"NOT_RUN", "SKIPPED"}:
            return status, f"미실행/제외: {status}"
    if kind in {"pytest-json", "node-json", "json-pair"}:
        if first.status == "PASS" and second.status == "PASS":
            return "PASS", "두 도구 PASS"
        return "FAIL", f"first={first.status}, second={second.status}"
    left = sorted(first.findings)
    right = sorted(second.findings)
    if left != right:
        return "FAIL", f"도구 결과 불일치 A={len(left)} B={len(right)}"
    if kind == "secret":
        if first.findings:
            return "FAIL", f"비밀값 {len(first.findings)}건"
        return "PASS", "고신뢰 비밀값 패턴 없음"
    if first.findings:
        return "PASS", f"인증 없는 매핑 {len(first.findings)}건을 두 도구가 같이 찾음"
    return "PASS", "인증 없는 매핑 없음"


def function_near(finding: str) -> tuple[str, str, str]:
    relative, number = finding.rsplit(":", 1)
    path = ROOT / relative
    if not path.is_file():
        return relative, "UNKNOWN", number
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(int(number) - 1, 0)
    for line in lines[start : start + 8]:
        matched = re.search(r"public\s+[\w<>,\[\] ?]+\s+(\w+)\s*\(", line)
        if matched:
            return relative, matched.group(1), number
        matched = re.search(r"def\s+(\w+)\s*\(", line)
        if matched:
            return relative, matched.group(1), number
    return relative, "UNKNOWN", number


def choose_auth_finding(findings: list[str]) -> str:
    for finding in findings:
        if "DiagnosisController.java" in finding and finding.endswith(":39"):
            return finding
    for finding in findings:
        if "DiagnosisController.java" in finding:
            return finding
    return findings[0]


def shlex_join(parts: list[str]) -> str:
    return " ".join(parts)


def outcome_row(run_id: str, commit: str, item: Outcome, evidence: str) -> dict:
    check = item.check
    return {
        "RUN_ID": run_id,
        "TC_ID": check.tc_id,
        "FEATURE_ID": check.feature_id,
        "REQUIREMENT_ID": check.requirement_id,
        "started_at": item.started_at,
        "ended_at": item.ended_at,
        "area": check.area,
        "section": check.section,
        "feature": check.feature,
        "test_type": check.test_type,
        "tool_a": check.tool_a,
        "command_a": shlex_join(check.cmd_a),
        "tool_a_result": item.tool_a.status,
        "tool_b": check.tool_b,
        "command_b": shlex_join(check.cmd_b),
        "tool_b_result": item.tool_b.status,
        "final_status": item.final,
        "expected_result": check.expected_result,
        "actual_result": item.note,
        "git_commit": commit,
        "file": item.tool_b.file or check.file,
        "function": item.tool_b.function or check.function,
        "line": item.line,
        "evidence_path": evidence,
        "issue_id": "",
        "risk_id": item.risk_id,
        "note": item.note,
    }


def section_md(title: str, lines: list[str]) -> str:
    return "\n".join([title, "", *lines])


def write_day(directory: Path, rows: list[dict], passes: list[str], fails: list[str], risks: list[str]) -> None:
    ensure_day_stubs(directory)
    # If legacy header exists, archive and start fresh for V3 columns
    results_path = directory / "results.tsv"
    if results_path.exists():
        with results_path.open(encoding="utf-8-sig", newline="") as handle:
            header = next(csv.reader(handle, delimiter="\t"), None)
        if header != COLUMNS:
            backup = directory / f"results_legacy_{secrets.token_hex(2)}.tsv"
            results_path.rename(backup)
            ensure_day_stubs(directory)
    append_results(directory, rows)
    append_md(directory, "pass.md", "PASS", "통과한 TC. 이전 절은 삭제하지 않는다.", passes)
    append_md(directory, "fail.md", "FAIL", "실패와 도구 오류. 해당 실행에 없으면 제목만 남는다.", fails)
    append_md(
        directory,
        "risk.md",
        "RISK",
        "잠재 위험 등록부. 실행 상태와 별개. 같은 RISK_ID의 마지막 처리상태가 현재 상태다.",
        risks,
    )
    sheet_rows: list[list[object]] = [list(COLUMNS)]
    with (directory / "results.tsv").open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            sheet_rows.append([row.get(name, "") for name in COLUMNS])
    write_xlsx(directory / "test_sheet.xlsx", {"Results": sheet_rows})


def write_master_xlsx(outcomes: list[Outcome] | None = None) -> None:
    by_tc = {item.check.tc_id: item for item in (outcomes or [])}
    overview: list[list[object]] = [
        [
            "area",
            "section",
            "tc_id",
            "feature_id",
            "final_status",
            "tool_a",
            "tool_a_result",
            "tool_b",
            "tool_b_result",
            "risk_id",
        ]
    ]
    latest: dict[str, dict[str, str]] = {}
    if RESULTS.exists():
        for path in sorted(RESULTS.glob("*/*/*/results.tsv")):
            with path.open(encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle, delimiter="\t"):
                    tc_id = (row.get("TC_ID") or "").strip()
                    if tc_id:
                        latest[tc_id] = row
    for tc_id, row in sorted(latest.items()):
        overview.append(
            [
                row.get("area", ""),
                row.get("section", ""),
                tc_id,
                row.get("FEATURE_ID", ""),
                row.get("final_status", ""),
                row.get("tool_a", ""),
                row.get("tool_a_result", ""),
                row.get("tool_b", ""),
                row.get("tool_b_result", ""),
                row.get("risk_id", ""),
            ]
        )
    for item in by_tc.values():
        if item.check.tc_id not in latest:
            overview.append(
                [
                    item.check.area,
                    item.check.section,
                    item.check.tc_id,
                    item.check.feature_id,
                    item.final,
                    item.check.tool_a,
                    item.tool_a.status,
                    item.check.tool_b,
                    item.tool_b.status,
                    item.risk_id,
                ]
            )

    stats: list[list[object]] = [["area", "pass", "fail", "blocked", "error", "not_run", "other"]]
    counts: dict[str, dict[str, int]] = {area: {} for area in AREAS}
    for row in overview[1:]:
        area = str(row[0])
        status = str(row[4]).lower()
        bucket = counts.setdefault(area, {})
        key = status if status in {"pass", "fail", "blocked", "error", "not_run"} else "other"
        bucket[key] = bucket.get(key, 0) + 1
    for area in AREAS:
        bucket = counts.get(area, {})
        stats.append(
            [
                area,
                bucket.get("pass", 0),
                bucket.get("fail", 0),
                bucket.get("blocked", 0),
                bucket.get("error", 0),
                bucket.get("not_run", 0),
                bucket.get("other", 0),
            ]
        )
    write_xlsx(MASTER_XLSX, {"LatestStatus": overview, "AreaStats": stats})


def build_outcomes(checks: list[Check]) -> list[Outcome]:
    outcomes: list[Outcome] = []
    for check in checks:
        started = datetime.now(SEOUL).strftime("%Y-%m-%dT%H:%M:%S+09:00")
        try:
            first, second = execute(check)
        except subprocess.TimeoutExpired as error:
            message = f"timeout: {error}"
            first = ToolOutput("ERROR", message)
            second = ToolOutput("ERROR", message)
        ended = datetime.now(SEOUL).strftime("%Y-%m-%dT%H:%M:%S+09:00")
        final, reason = decide(check.kind, first, second)
        line = line_of(second.file or check.file, second.line_needle or check.line_needle)
        if line == "UNKNOWN":
            line = line_of(check.file, check.line_needle)
        note = " | ".join(
            [
                check.scope,
                f"A `{shlex_join(check.cmd_a)}` {first.summary}",
                f"B `{shlex_join(check.cmd_b)}` {second.summary}",
                reason,
            ]
        )
        risk_md = ""
        risk_id = ""
        if check.kind == "auth" and final == "PASS" and first.findings:
            chosen = choose_auth_finding(first.findings)
            path, function, found_line = function_near(chosen)
            line = found_line
            risk_id = "RISK-SEC-001"
            risk_md = "\n".join(
                [
                    "## {run_id} RISK-SEC-001",
                    "",
                    "- RISK_ID: RISK-SEC-001",
                    "- TC_ID: QA-SEC-AUTH-001",
                    "- 실행시각: {when}",
                    "- 심각도: HIGH",
                    "- 발생가능성: HIGH",
                    "- 영향: 진단·추천·RAG API에 인증 표시가 없다.",
                    "- 처리상태: OPEN",
                    "- 권장조치: 접근 정책 확정 전 완료로 보지 않는다.",
                    f"- 파일: {path}",
                    f"- 함수: {function}",
                    f"- 줄번호: {found_line}",
                    "- ISSUE_ID: ",
                    f"- 근거: 목록={', '.join(first.findings)}",
                ]
            )
        if check.tc_id in {"QA-UNIT-FRONT-001", "QA-E2E-FLOW-001"} and final == "PASS":
            risk_id = risk_id or "RISK-V3-PLAYWRIGHT"
            risk_md = (
                risk_md
                + ("\n\n" if risk_md else "")
                + "\n".join(
                    [
                        "## {run_id} RISK-V3-PLAYWRIGHT",
                        "",
                        "- RISK_ID: RISK-V3-PLAYWRIGHT",
                        f"- TC_ID: {check.tc_id}",
                        "- 실행시각: {when}",
                        "- 심각도: MEDIUM",
                        "- 발생가능성: MEDIUM",
                        "- 영향: V3 목표 도구인 Playwright가 아직 기본 경로가 아니다. 현재는 node --test/E2E와 독립 Python 검증을 사용한다.",
                        "- 처리상태: OPEN",
                        "- 권장조치: Playwright 스모크를 front에 추가하고 test_map 1차 도구를 교체한다.",
                        "- 파일: front/package.json",
                        "- 함수: UNKNOWN",
                        "- 줄번호: UNKNOWN",
                        "- ISSUE_ID: ",
                        "- 근거: test_map.json 02_web_api note",
                    ]
                )
            )
        if check.tc_id == "QA-SEC-SEMGREP-001" and final == "PASS":
            risk_id = "RISK-V3-CODEQL"
            risk_md = "\n".join(
                [
                    "## {run_id} RISK-V3-CODEQL",
                    "",
                    "- RISK_ID: RISK-V3-CODEQL",
                    "- TC_ID: QA-SEC-SEMGREP-001",
                    "- 실행시각: {when}",
                    "- 심각도: MEDIUM",
                    "- 발생가능성: LOW",
                    "- 영향: 로컬 2차는 secret-grep이다. CodeQL은 GitHub Actions codeql job이 공식 병행 경로다.",
                    "- 처리상태: OPEN",
                    "- 권장조치: CI CodeQL required check를 브랜치 보호에 포함한다.",
                    "- 파일: .github/workflows/ci.yml",
                    "- 함수: UNKNOWN",
                    "- 줄번호: UNKNOWN",
                    "- ISSUE_ID: ",
                    "- 근거: V3 03_security_quality CodeQL+Semgrep",
                ]
            )
        outcomes.append(
            Outcome(check, first, second, final, note, line, started, ended, risk_md, risk_id)
        )
    return outcomes


def ensure_section_dirs(checks: list[Check]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    for area in AREAS:
        (RESULTS / area).mkdir(parents=True, exist_ok=True)
    for check in checks:
        (RESULTS / check.area / check.section).mkdir(parents=True, exist_ok=True)
    HISTORY.parent.mkdir(parents=True, exist_ok=True)


def render(run_id: str, when: str, commit: str, outcomes: list[Outcome]) -> int:
    grouped: dict[tuple[str, str], list[tuple[dict, str, str, str]]] = {}

    def add(area: str, section: str, row: dict, passed: str, failed: str, risk: str) -> None:
        grouped.setdefault((area, section), []).append((row, passed, failed, risk))

    history_rows: list[dict] = []
    for item in outcomes:
        day = item.ended_at[:10]
        evidence = str((RESULTS / item.check.area / item.check.section / day).relative_to(ROOT))
        row = outcome_row(run_id, commit, item, evidence)
        history_rows.append(row)
        passed = failed = ""
        risk = item.risk_md.replace("{run_id}", run_id).replace("{when}", when) if item.risk_md else ""
        heading = f"## {run_id} {item.check.tc_id}"
        common = [
            f"- TC_ID: {item.check.tc_id}",
            f"- FEATURE_ID: {item.check.feature_id}",
            f"- REQUIREMENT_ID: {item.check.requirement_id}",
            f"- 실행시각: {item.started_at} ~ {item.ended_at}",
            f"- area: {item.check.area}",
            f"- section: {item.check.section}",
            f"- 도구A: {item.check.tool_a} / {item.tool_a.status} / {shlex_join(item.check.cmd_a)}",
            f"- 도구B: {item.check.tool_b} / {item.tool_b.status} / {shlex_join(item.check.cmd_b)}",
            f"- 기대결과: {item.check.expected_result}",
            f"- 실제결과: {item.note}",
            f"- 증거: {evidence}",
            f"- GitCommit: {commit}",
            f"- 파일: {row['file']}",
            f"- 함수: {row['function']}",
            f"- 줄번호: {row['line']}",
            f"- RISK_ID: {item.risk_id}",
        ]
        if item.final == "PASS":
            passed = section_md(heading, common + ["- 검증목적: 서로 다른 두 경로의 필수 단언 통과"])
        else:
            failed = section_md(
                heading,
                common
                + [
                    f"- 오류: {item.tool_a.summary} / {item.tool_b.summary}",
                    f"- 재현: {shlex_join(item.check.cmd_a)} ; {shlex_join(item.check.cmd_b)}",
                    f"- 도구A출력: {item.tool_a.detail or item.tool_a.summary}",
                    f"- 도구B출력: {item.tool_b.detail or item.tool_b.summary}",
                    "- 원인: UNKNOWN",
                    "- 수정위치: UNKNOWN",
                    "- 재검증: 아직 없음",
                ],
            )
        add(item.check.area, item.check.section, row, passed, failed, risk)

    for (area, section), entries in grouped.items():
        day = entries[0][0]["ended_at"][:10]
        directory = RESULTS / area / section / day
        write_day(
            directory,
            [e[0] for e in entries],
            [e[1] for e in entries if e[1]],
            [e[2] for e in entries if e[2]],
            [e[3] for e in entries if e[3]],
        )

    append_history(HISTORY, history_rows)
    write_master_xlsx(outcomes)

    counts = {"PASS": 0, "FAIL": 0, "BLOCKED": 0, "ERROR": 0, "NOT_RUN": 0, "SKIPPED": 0}
    print(f"RUN_ID {run_id}")
    for item in outcomes:
        counts[item.final] = counts.get(item.final, 0) + 1
        print(f"{item.check.tc_id} {item.final} {item.check.area}/{item.check.section}")
    print(
        "SUMMARY "
        f"total={len(outcomes)} "
        + " ".join(f"{k}={counts.get(k, 0)}" for k in ("PASS", "FAIL", "BLOCKED", "ERROR", "NOT_RUN", "SKIPPED"))
    )

    result = evaluate(RESULTS, required_ids())
    if result.ok:
        print("GATE PASS")
        return 0
    print("GATE FAIL")
    for reason in result.reasons:
        print(f"- {reason}")
    return 1


def filter_checks(checks: list[Check], area: str | None, section: str | None, tc_id: str | None) -> list[Check]:
    selected = checks
    if area:
        selected = [item for item in selected if item.area == area]
    if section:
        selected = [item for item in selected if item.section == section]
    if tc_id:
        selected = [item for item in selected if item.tc_id == tc_id]
    if not selected:
        raise SystemExit("선택한 area/section/TC에 해당하는 검사가 없습니다.")
    return selected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run pivotSeoul V3 QA checks.")
    parser.add_argument("--profile", choices=("required", "regression"), default="required")
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--area", choices=AREAS, default=None)
    parser.add_argument("--section", default=None)
    parser.add_argument("--tc", default=None)
    args = parser.parse_args(argv)
    if not TEST_MAP.exists():
        raise SystemExit(f"missing {TEST_MAP}")
    all_checks = checks_for(args.profile)
    ensure_section_dirs(all_checks)
    selected = filter_checks(all_checks, args.area, args.section, args.tc)
    now = datetime.now(SEOUL)
    run_id = f"R{now:%Y%m%d-%H%M%S}-{secrets.token_hex(2)}"
    when = now.strftime("%Y-%m-%dT%H:%M:%S+09:00")
    commit = git_commit()
    outcomes = build_outcomes(selected)
    code = render(run_id, when, commit, outcomes)
    # drop obsolete master tsv if present (V3: xlsx only at root)
    legacy = QA_ROOT / "master_test_sheet.tsv"
    if legacy.exists():
        legacy.unlink()
    if args.gate:
        return code
    return 0 if all(item.final == "PASS" for item in outcomes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
