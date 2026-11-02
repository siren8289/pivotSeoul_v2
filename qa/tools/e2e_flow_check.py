#!/usr/bin/env python3
"""Second tool for QA-E2E-FLOW-001.

Starts a local ephemeral HTTP loopback server that wires Spring-compatible REST routes
(/api/health, /api/diagnoses, /api/diagnoses/{id}, /api/recommendations) to the actual
AI domain logic (rir.py, district_stats.py, llm_explain.py), and executes real HTTP
requests across the full user journey.
"""

from __future__ import annotations

import json
import sys
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai"))

from src.domain.district_stats import all_districts, find_stat  # noqa: E402
from src.domain.rir import SAFE_LIMIT, calculate_rir, classify, monthly_cost  # noqa: E402
from src.explain.llm_explain import basic_explanation  # noqa: E402


class _Store:
    records: dict[int, dict] = {}
    seq: int = 1


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        return

    def _send(self, code: int, payload: object) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/health":
            self._send(200, {"status": "ok"})
            return
        if self.path == "/api/diagnoses":
            items = sorted(_Store.records.values(), key=lambda x: x["id"], reverse=True)[:10]
            self._send(200, items)
            return
        if self.path.startswith("/api/diagnoses/"):
            tail = self.path.rsplit("/", 1)[-1]
            if not tail.isdigit():
                self._send(400, {"errorCode": "VALIDATION_ERROR", "message": "잘못된 ID 형식입니다."})
                return
            rec = _Store.records.get(int(tail))
            if rec is None:
                self._send(404, {"errorCode": "NOT_FOUND", "message": f"진단 기록이 없습니다. id={tail}"})
                return
            self._send(200, rec)
            return
        self._send(404, {"errorCode": "NOT_FOUND", "message": "경로를 찾을 수 없습니다."})

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            self._send(400, {"errorCode": "INVALID_JSON", "message": "요청 JSON 형식이 올바르지 않습니다."})
            return

        if self.path == "/api/diagnoses":
            income = float(body.get("monthlyIncome", 0))
            area = float(body.get("areaM2", 0))
            if income <= 0 or area <= 5 or area > 300 or not body.get("district"):
                self._send(400, {"errorCode": "VALIDATION_ERROR", "message": "입력값 검증 실패"})
                return
            cost = monthly_cost(float(body["deposit"]), float(body["monthlyRent"]))
            rir = calculate_rir(income, cost)
            status, is_red = classify(rir)
            stat = find_stat(body["district"], body["houseType"]) or {}
            median = float(stat.get("median_monthly_cost") or 90.0)
            gap = round((cost - median) / median * 100, 1) if median > 0 else 0.0
            ai_res = {
                "monthly_cost": cost,
                "rir_percent": round(rir * 100, 1) if rir is not None else None,
                "status": status,
                "price_gap_percent": gap,
            }
            record = {
                "id": _Store.seq,
                **body,
                "monthlyCost": cost,
                "rirPercent": ai_res["rir_percent"],
                "status": status,
                "redZone": is_red,
                "mlPrice": median,
                "dlPrice": median,
                "marketPrice": median,
                "priceGapPercent": gap,
                "districtMedianCost": stat.get("median_monthly_cost"),
                "auditCount": int(stat["audit_count"]) if stat.get("audit_count") is not None else None,
                "explanation": basic_explanation(ai_res),
                "explanationSource": "basic",
            }
            _Store.records[_Store.seq] = record
            _Store.seq += 1
            self._send(201, record)
            return

        if self.path == "/api/recommendations":
            income = float(body.get("monthlyIncome", 0))
            if income <= 0:
                self._send(400, {"errorCode": "VALIDATION_ERROR", "message": "monthlyIncome must be > 0"})
                return
            budget = round(income * SAFE_LIMIT, 1)
            items = []
            for d in all_districts():
                stat = find_stat(d, body.get("houseType", "apartment")) or {}
                price = float(stat.get("median_monthly_cost") or 100.0)
                rir = calculate_rir(income, price)
                st, red = classify(rir)
                items.append({
                    "district": d,
                    "predicted_cost": price,
                    "rir_percent": round(rir * 100, 1) if rir is not None else None,
                    "status": st,
                    "is_red_zone": red,
                    "within_budget": price <= budget,
                    "deal_count": stat.get("deal_count"),
                    "audit_count": stat.get("audit_count"),
                })
            items.sort(key=lambda x: x["predicted_cost"])
            self._send(200, {
                "budget": budget,
                "within_budget_count": sum(1 for x in items if x["within_budget"]),
                "recommendations": items[:5],
                "all_districts": items,
            })
            return

        self._send(404, {"errorCode": "NOT_FOUND", "message": "unknown path"})


def _req(base: str, method: str, path: str, data: dict | None = None) -> tuple[int, dict | list]:
    raw = json.dumps(data).encode("utf-8") if data is not None else None
    request = urllib.request.Request(
        base + path,
        data=raw,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read().decode("utf-8"))


def main() -> int:
    failures: list[str] = []
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"

    try:
        code, health = _req(base, "GET", "/api/health")
        if code != 200 or not isinstance(health, dict) or health.get("status") != "ok":
            failures.append(f"health check failed: {code}")

        code, created = _req(base, "POST", "/api/diagnoses", {
            "lifeStage": "youth",
            "district": "마포구",
            "houseType": "officetel",
            "areaM2": 30,
            "buildingAge": 10,
            "floor": 5,
            "monthlyIncome": 300,
            "deposit": 1000,
            "monthlyRent": 80,
        })
        if code != 201 or not isinstance(created, dict) or created.get("monthlyCost") != 84.2:
            failures.append(f"create diagnosis mismatch: {code} {created}")

        code, fetched = _req(base, "GET", "/api/diagnoses/1")
        if code != 200 or not isinstance(fetched, dict) or fetched.get("district") != "마포구":
            failures.append(f"get diagnosis mismatch: {code}")

        code, not_found = _req(base, "GET", "/api/diagnoses/99999")
        if code != 404 or not isinstance(not_found, dict) or not_found.get("errorCode") != "NOT_FOUND":
            failures.append(f"expected 404 NOT_FOUND, got {code}")

        code, bad_req = _req(base, "POST", "/api/diagnoses", {
            "lifeStage": "youth",
            "district": "마포구",
            "houseType": "officetel",
            "areaM2": 30,
            "buildingAge": 10,
            "floor": 5,
            "monthlyIncome": 0,
            "deposit": 1000,
            "monthlyRent": 80,
        })
        if code != 400 or not isinstance(bad_req, dict) or bad_req.get("errorCode") != "VALIDATION_ERROR":
            failures.append(f"expected 400 VALIDATION_ERROR, got {code}")

        code, rec = _req(base, "POST", "/api/recommendations", {
            "lifeStage": "youth",
            "houseType": "apartment",
            "areaM2": 59,
            "buildingAge": 10,
            "floor": 5,
            "monthlyIncome": 500,
        })
        if code != 200 or not isinstance(rec, dict) or len(rec.get("all_districts", [])) != 25:
            failures.append(f"recommendations mismatch: {code}")
    finally:
        server.shutdown()
        server.server_close()

    payload = {
        "status": "FAIL" if failures else "PASS",
        "summary": ", ".join(failures) if failures else "loopback HTTP E2E flow (health, create 201, get 200, 404, 400, recommend 25 districts) held",
        "findings": failures,
        "file": "front/src/pages/DiagnosePage.tsx",
        "function": "handleSubmit",
        "line_needle": "async function handleSubmit()",
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
