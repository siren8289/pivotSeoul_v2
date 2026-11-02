#!/usr/bin/env python3
"""Block a finished turn when code changed and QA reports are older than that code."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE_PREFIXES = (
    "ai/",
    "back/",
    "front/",
    "data/",
    "scripts/",
    "qa/run_qa.py",
    "qa/record.py",
    "qa/gate.py",
    "qa/tools/",
    "qa/hooks/",
    "qa/tests/",
    ".github/workflows/",
)
CODE_FILES = {"compose.yaml", "compose.yaml.bak"}
REASON = (
    "코드 변경 이후 QA 기록이 없습니다. "
    "python qa/run_qa.py --profile required --gate 를 실행하고 qa/reports를 갱신한 뒤, "
    "미해결 HIGH/CRITICAL을 사용자에게 보고하세요. 실행하지 않은 테스트는 PASS로 적지 마세요."
)


def is_code_path(path: str) -> bool:
    if path.startswith("qa/reports/"):
        return False
    if path in CODE_FILES or path.startswith("compose.yaml"):
        return True
    return any(path.startswith(prefix) for prefix in CODE_PREFIXES)


def should_block(event: dict, changed: list[str], report_mtime: float | None, code_mtime: float | None) -> str | None:
    if event.get("stopHookActive") or event.get("stop_hook_active"):
        return None
    reason = event.get("reason")
    if reason and reason != "end_turn":
        return None
    if not [path for path in changed if is_code_path(path)]:
        return None
    if report_mtime is None or (code_mtime is not None and code_mtime > report_mtime):
        return REASON
    return None


def changed_files() -> list[str]:
    names: set[str] = set()
    commands = (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode == 0:
            names.update(line.strip() for line in result.stdout.splitlines() if line.strip())
    return sorted(names)


def latest_mtime(paths: list[Path]) -> float | None:
    times = [path.stat().st_mtime for path in paths if path.exists()]
    if not times:
        return None
    return max(times)


def main() -> int:
    raw = sys.stdin.read().strip()
    event = json.loads(raw) if raw else {}
    changed = changed_files()
    code_paths = [ROOT / path for path in changed if is_code_path(path)]
    reports = list((ROOT / "qa" / "reports").glob("*/*/results.tsv")) if (ROOT / "qa" / "reports").exists() else []
    message = should_block(event, changed, latest_mtime(reports), latest_mtime(code_paths))
    if message:
        json.dump({"decision": "block", "reason": message}, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
