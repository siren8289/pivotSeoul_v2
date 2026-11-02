#!/usr/bin/env python3
"""Run required QA checks with two tools and append dated reports."""

from __future__ import annotations

import argparse
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
from qa.record import append_md, append_results  # noqa: E402
REPORTS = ROOT / "qa" / "reports"
SEOUL = ZoneInfo("Asia/Seoul")
REQUIRED_IDS = [
    "QA-UNIT-DATA-001",
    "QA-UNIT-RECORD-001",
    "QA-SEC-SECRET-001",
    "QA-SEC-AUTH-001",
]


@dataclass
class Check:
    tc_id: str
    feature: str
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
    risk_md: str = ""


def checks_for(profile: str) -> list[Check]:
    python = sys.executable
    items = [
        Check(
            tc_id="QA-UNIT-DATA-001",
            feature="data-etl",
            test_type="unit",
            tool_a="pytest",
            cmd_a=[python, "-m", "pytest", "data/tests", "-q", "--tb=line"],
            tool_b="invariant-check",
            cmd_b=[python, "qa/tools/invariant_check.py"],
            kind="pytest-json",
            file="data/etl/transform.py",
            function="calc_monthly_cost",
            line_needle="def calc_monthly_cost",
            scope="pytest는 data/tests 전체. invariant-check는 월 환산 주거비, 빈 주소, as_list만 본다.",
            required=True,
        ),
        Check(
            tc_id="QA-UNIT-RECORD-001",
            feature="qa-recorder",
            test_type="unit",
            tool_a="pytest",
            cmd_a=[python, "-m", "pytest", "qa/tests", "-q", "--tb=line"],
            tool_b="record-selfcheck",
            cmd_b=[python, "qa/tools/record_selfcheck.py"],
            kind="pytest-json",
            file="qa/record.py",
            function="append_results",
            line_needle="def append_results",
            scope="pytest는 qa/tests. record-selfcheck는 누적 기록, BOM, PASS 규칙, HIGH 게이트를 pytest 없이 확인한다.",
            required=True,
        ),
        Check(
            tc_id="QA-SEC-SECRET-001",
            feature="secrets",
            test_type="security",
            tool_a="secret-scan",
            cmd_a=[python, "qa/tools/secret_scan.py"],
            tool_b="secret-grep",
            cmd_b=[python, "qa/tools/secret_grep.py"],
            kind="secret",
            file="qa/tools/secret_scan.py",
            function="scan",
            line_needle="def scan",
            scope="추적 중인 텍스트 파일의 개인키, AKIA, AIza, ghp_ 패턴. 두 도구가 패턴을 각자 가진다.",
            required=True,
        ),
        Check(
            tc_id="QA-SEC-AUTH-001",
            feature="api-auth",
            test_type="security",
            tool_a="auth-surface",
            cmd_a=[python, "qa/tools/auth_surface.py"],
            tool_b="auth-grep",
            cmd_b=[python, "qa/tools/auth_grep.py"],
            kind="auth",
            file="back/src/main/java/com/pivotseoul/diagnosis/controller/DiagnosisController.java",
            function="get",
            line_needle='@GetMapping("/{id}")',
            scope="back/src/main 과 ai/src 의 매핑. /health 는 상태 확인이라 제외한다. 인증 정책이 없어 발견은 RISK다.",
            required=True,
        ),
    ]
    if profile == "regression":
        for item in items:
            item.test_type = "regression"
        return items
    if profile != "required":
        raise SystemExit(f"unknown profile: {profile}")
    return items


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
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )


def tail(text: str, limit: int = 1200) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[:limit] + "…"


def parse_json_tool(completed: subprocess.CompletedProcess[str]) -> ToolOutput:
    detail = tail(completed.stdout + "\n" + completed.stderr)
    if completed.returncode != 0:
        return ToolOutput("ERROR", f"exit {completed.returncode}", detail=detail)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return ToolOutput("ERROR", "JSON이 아닙니다.", detail=detail)
    status = payload.get("status", "ERROR")
    if status not in {"PASS", "FAIL", "ERROR"}:
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


def execute(check: Check) -> tuple[ToolOutput, ToolOutput]:
    first = run_command(check.cmd_a)
    second = run_command(check.cmd_b)
    if check.kind == "pytest-json":
        return parse_pytest(first), parse_json_tool(second)
    return parse_json_tool(first), parse_json_tool(second)


def decide(kind: str, first: ToolOutput, second: ToolOutput) -> tuple[str, str]:
    if first.status == "ERROR" or second.status == "ERROR":
        return "ERROR", "도구 실행 오류"
    if kind == "pytest-json":
        if first.status == "PASS" and second.status == "PASS":
            return "PASS", "두 도구 PASS"
        return "FAIL", f"pytest={first.status}, second={second.status}"
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
    for line in lines[start:start + 8]:
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


def front_inventory() -> tuple[str, str, str]:
    package = ROOT / "front" / "package.json"
    if not package.is_file():
        return "NOT_RUN", "UNKNOWN", "front/package.json 이 없습니다."
    payload = json.loads(package.read_text(encoding="utf-8"))
    scripts = payload.get("scripts", {})
    line = line_of("front/package.json", '"scripts"')
    if "test" not in scripts:
        return "NOT_RUN", line, "front/package.json에 test 스크립트가 없다. 프론트 테스트는 실행하지 않았다."
    return "SKIPPED", line, "front test 스크립트는 있으나 이 프로필에서 실행하지 않았다."


def blank_row(run_id: str, when: str, commit: str, check: Check, final: str, line: str, note: str, risk_id: str = "") -> dict:
    return {
        "RUN_ID": run_id,
        "TC_ID": check.tc_id,
        "실행시각": when,
        "기능명": check.feature,
        "테스트종류": check.test_type,
        "도구A": check.tool_a,
        "도구A결과": "NOT_RUN",
        "도구B": check.tool_b,
        "도구B결과": "NOT_RUN",
        "최종상태": final,
        "GitCommit": commit,
        "파일": check.file,
        "함수": check.function,
        "줄번호": line,
        "ISSUE_ID": "",
        "RISK_ID": risk_id,
        "비고": note,
    }


def outcome_row(run_id: str, when: str, commit: str, item: Outcome, risk_id: str) -> dict:
    check = item.check
    location_file = item.tool_b.file or check.file
    location_function = item.tool_b.function or check.function
    return {
        "RUN_ID": run_id,
        "TC_ID": check.tc_id,
        "실행시각": when,
        "기능명": check.feature,
        "테스트종류": check.test_type,
        "도구A": check.tool_a,
        "도구A결과": item.tool_a.status,
        "도구B": check.tool_b,
        "도구B결과": item.tool_b.status,
        "최종상태": item.final,
        "GitCommit": commit,
        "파일": location_file,
        "함수": location_function,
        "줄번호": item.line,
        "ISSUE_ID": "",
        "RISK_ID": risk_id,
        "비고": item.note,
    }


def section(title: str, lines: list[str]) -> str:
    return "\n".join([title, "", *lines])


def write_type(directory: Path, rows: list[dict], passes: list[str], fails: list[str], risks: list[str]) -> None:
    append_results(directory, rows)
    append_md(directory, "pass.md", "PASS", "통과한 TC. 이전 절은 삭제하지 않는다.", passes)
    append_md(directory, "fail.md", "FAIL", "실패와 도구 오류. 해당 실행에 없으면 제목만 남는다.", fails)
    append_md(directory, "risk.md", "RISK", "잠재 위험. 같은 RISK_ID의 마지막 처리상태가 현재 상태다.", risks)


def build_outcomes(profile: str) -> tuple[list[Outcome], list[dict]]:
    outcomes: list[Outcome] = []
    for check in checks_for(profile):
        try:
            first, second = execute(check)
        except subprocess.TimeoutExpired as error:
            message = f"timeout: {error}"
            first = ToolOutput("ERROR", message)
            second = ToolOutput("ERROR", message)
        final, reason = decide(check.kind, first, second)
        line = line_of(second.file or check.file, second.line_needle or check.line_needle)
        if line == "UNKNOWN":
            line = line_of(check.file, check.line_needle)
        note = " | ".join([
            check.scope,
            f"A `{shlex_join(check.cmd_a)}` {first.summary}",
            f"B `{shlex_join(check.cmd_b)}` {second.summary}",
            reason,
        ])
        risk_md = ""
        if check.kind == "auth" and final == "PASS" and first.findings:
            chosen = choose_auth_finding(first.findings)
            path, function, found_line = function_near(chosen)
            line = found_line
            listed = ", ".join(first.findings)
            risk_md = "\n".join([
                "## {run_id} RISK-SEC-001",
                "",
                "- RISK_ID: RISK-SEC-001",
                "- TC_ID: QA-SEC-AUTH-001",
                "- 실행시각: {when}",
                "- 심각도: HIGH",
                "- 발생가능성: HIGH",
                "- 영향: 진단·추천·RAG API에 인증 표시가 없다. Diagnosis.monthlyIncome은 저장되고 id는 IDENTITY로 증가한다. 권한 정책은 확정되어 있지 않아 결함으로 단정하지 않는다.",
                "- 처리상태: OPEN",
                "- 권장조치: 접근 정책을 정하기 전에는 완료로 보지 않는다. 인증을 넣거나, 공개 범위와 식별자 정책을 정한 뒤 ACCEPTED로 남긴다.",
                f"- 파일: {path}",
                f"- 함수: {function}",
                f"- 줄번호: {found_line}",
                "- ISSUE_ID: ",
                "- 근거: 두 도구의 매핑 목록이 같다. /health 는 제외했다. "
                f"monthlyIncome 줄 {line_of('back/src/main/java/com/pivotseoul/diagnosis/entity/Diagnosis.java', 'private double monthlyIncome')}, "
                f"@GeneratedValue 줄 {line_of('back/src/main/java/com/pivotseoul/diagnosis/entity/Diagnosis.java', '@GeneratedValue')}. "
                f"목록: {listed}",
            ])
            outcomes.append(Outcome(check, first, second, final, note, line, risk_md))
            continue
        outcomes.append(Outcome(check, first, second, final, note, line, ""))
    return outcomes, []


def shlex_join(parts: list[str]) -> str:
    return " ".join(parts)


def render(run_id: str, when: str, commit: str, outcomes: list[Outcome], profile: str) -> int:
    front_status, front_line, front_note = front_inventory()
    front = Check(
        tc_id="QA-UNIT-FRONT-001",
        feature="front",
        test_type="regression" if profile == "regression" else "unit",
        tool_a="none",
        cmd_a=[],
        tool_b="none",
        cmd_b=[],
        kind="inventory",
        file="front/package.json",
        function="UNKNOWN",
        line_needle='"scripts"',
        scope="프론트 테스트 러너가 있는지 확인만 한다.",
        required=False,
    )
    grouped: dict[str, list[tuple[dict, str, str, str]]] = {}

    def add(test_type: str, row: dict, passed: str, failed: str, risk: str) -> None:
        grouped.setdefault(test_type, []).append((row, passed, failed, risk))

    for item in outcomes:
        risk_id = "RISK-SEC-001" if item.risk_md else ""
        row = outcome_row(run_id, when, commit, item, risk_id)
        passed = ""
        failed = ""
        risk = item.risk_md.replace("{run_id}", run_id).replace("{when}", when) if item.risk_md else ""
        heading = f"## {run_id} {item.check.tc_id}"
        common = [
            f"- TC_ID: {item.check.tc_id}",
            f"- 실행시각: {when}",
            f"- 기능명: {item.check.feature}",
            f"- 도구A: {item.check.tool_a} / {item.tool_a.status} / {shlex_join(item.check.cmd_a)}",
            f"- 도구B: {item.check.tool_b} / {item.tool_b.status} / {shlex_join(item.check.cmd_b)}",
            f"- 범위: {item.check.scope}",
            f"- GitCommit: {commit}",
            f"- 파일: {row['파일']}",
            f"- 함수: {row['함수']}",
            f"- 줄번호: {row['줄번호']}",
            "- ISSUE_ID: ",
            f"- RISK_ID: {risk_id}",
        ]
        if item.final == "PASS":
            passed = section(heading, common + [
                "- 검증목적: 두 도구의 필수 검사가 기대와 맞는지 확인한다.",
                f"- 기대결과: {item.check.scope}",
                f"- 실제결과: {item.note}",
            ])
        else:
            failed = section(heading, common + [
                f"- 입력값: {shlex_join(item.check.cmd_a)} ; {shlex_join(item.check.cmd_b)}",
                f"- 오류: {item.tool_a.summary} / {item.tool_b.summary}",
                f"- 재현: {shlex_join(item.check.cmd_a)}",
                f"- 기대결과: 두 도구 PASS 또는, 인증 표면은 동일 목록",
                f"- 실제결과: {item.note}",
                f"- 도구A출력: {item.tool_a.detail or item.tool_a.summary}",
                f"- 도구B출력: {item.tool_b.detail or item.tool_b.summary}",
                "- 원인: UNKNOWN",
                "- 수정위치: UNKNOWN",
                "- 재검증: 아직 없음",
            ])
        add(item.check.test_type, row, passed, failed, risk)

    front_risk = ""
    front_risk_id = ""
    if front_status == "NOT_RUN":
        front_risk_id = "RISK-QA-001"
        front_risk = "\n".join([
            f"## {run_id} RISK-QA-001",
            "",
            "- RISK_ID: RISK-QA-001",
            "- TC_ID: QA-UNIT-FRONT-001",
            f"- 실행시각: {when}",
            "- 심각도: MEDIUM",
            "- 발생가능성: HIGH",
            "- 영향: 화면 변경의 회귀를 자동 테스트로 확인하지 못한다.",
            "- 처리상태: OPEN",
            "- 권장조치: 프론트 테스트 도구를 정한 뒤 unit 또는 e2e를 두 도구로 실행한다. 도구는 아직 정하지 않았다.",
            "- 파일: front/package.json",
            "- 함수: UNKNOWN",
            f"- 줄번호: {front_line}",
            "- ISSUE_ID: ",
            f"- 근거: {front_note}",
        ])
    front_row = blank_row(run_id, when, commit, front, front_status, front_line, front_note, front_risk_id)
    add(front.test_type, front_row, "", "", front_risk)

    day = when[:10]
    for test_type, entries in grouped.items():
        directory = REPORTS / test_type / day
        write_type(
            directory,
            [entry[0] for entry in entries],
            [entry[1] for entry in entries if entry[1]],
            [entry[2] for entry in entries if entry[2]],
            [entry[3] for entry in entries if entry[3]],
        )
    print(f"RUN_ID {run_id}")
    for entries in grouped.values():
        for row, _passed, _failed, _risk in entries:
            print(f"{row['TC_ID']} {row['최종상태']} {row['테스트종류']}")
    result = evaluate(REPORTS, REQUIRED_IDS)
    if result.ok:
        print("GATE PASS")
        return 0
    print("GATE FAIL")
    for reason in result.reasons:
        print(f"- {reason}")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run pivotSeoul QA checks and append reports.")
    parser.add_argument("--profile", choices=("required", "regression"), default="required")
    parser.add_argument("--gate", action="store_true", help="Fail when required checks or blocking risks are open.")
    args = parser.parse_args(argv)
    now = datetime.now(SEOUL)
    run_id = f"R{now:%Y%m%d-%H%M%S}-{secrets.token_hex(2)}"
    when = now.strftime("%Y-%m-%dT%H:%M:%S+09:00")
    commit = git_commit()
    outcomes, _unused = build_outcomes(args.profile)
    return render(run_id, when, commit, outcomes, args.profile)


if __name__ == "__main__":
    raise SystemExit(main())
