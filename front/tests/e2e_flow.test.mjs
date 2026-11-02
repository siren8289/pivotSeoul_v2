import assert from "node:assert/strict";
import test from "node:test";
import {
  createDiagnosis,
  getDiagnosis,
  getRecommendations,
} from "../src/api/api.ts";
import { DISTRICTS, STATUS_INFO } from "../src/components/options.ts";

test("E2E user journey: 진단 생성 → 결과 조회 → 25개 자치구 추천 → 예외 응답 검증", async () => {
  const originalFetch = globalThis.fetch;
  const store = new Map();
  let seq = 1;

  try {
    globalThis.fetch = async (url, options = {}) => {
      const u = new URL(String(url));
      const body = options.body ? JSON.parse(String(options.body)) : null;

      if (u.pathname === "/api/diagnoses" && options.method === "POST") {
        if (!body || Number(body.monthlyIncome) <= 0 || Number(body.areaM2) <= 5) {
          return new Response(
            JSON.stringify({
              errorCode: "VALIDATION_ERROR",
              message: "monthlyIncome: 0보다 커야 합니다",
            }),
            { status: 400, headers: { "Content-Type": "application/json" } }
          );
        }
        const monthlyCost = Number(
          (body.monthlyRent + (body.deposit * 0.05) / 12).toFixed(1)
        );
        const rir = monthlyCost / body.monthlyIncome;
        const rirPercent = Number((rir * 100).toFixed(1));
        const status =
          rir <= 0.3 ? "stable" : rir <= 0.4 ? "warning" : "danger";
        const record = {
          ...body,
          id: seq++,
          monthlyCost,
          rirPercent,
          status,
          redZone: status === "danger",
          mlPrice: 90.0,
          dlPrice: 88.0,
          marketPrice: 89.0,
          priceGapPercent: Number(
            (((monthlyCost - 89.0) / 89.0) * 100).toFixed(1)
          ),
          districtMedianCost: 95.0,
          auditCount: 12,
          explanation: `소득 대비 주거비 비율은 ${rirPercent}%입니다.`,
          explanationSource: "basic",
        };
        store.set(String(record.id), record);
        return new Response(JSON.stringify(record), {
          status: 201,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (u.pathname.startsWith("/api/diagnoses/")) {
        const id = u.pathname.split("/").pop();
        const found = store.get(id);
        if (!found) {
          return new Response(
            JSON.stringify({
              errorCode: "NOT_FOUND",
              message: `진단 기록이 없습니다. id=${id}`,
            }),
            { status: 404, headers: { "Content-Type": "application/json" } }
          );
        }
        return new Response(JSON.stringify(found), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (u.pathname === "/api/recommendations" && options.method === "POST") {
        const budget = Number((body.monthlyIncome * 0.3).toFixed(1));
        const all = DISTRICTS.map((d, idx) => {
          const cost = 60 + idx * 4;
          const rirPct = Number(((cost / body.monthlyIncome) * 100).toFixed(1));
          return {
            district: d,
            predicted_cost: cost,
            rir_percent: rirPct,
            status: cost <= budget ? "stable" : "warning",
            is_red_zone: rirPct > 40,
            within_budget: cost <= budget,
            deal_count: 100 + idx,
            audit_count: 5 + idx,
          };
        }).sort((a, b) => a.predicted_cost - b.predicted_cost);
        const within = all.filter((x) => x.within_budget);
        return new Response(
          JSON.stringify({
            budget,
            within_budget_count: within.length,
            recommendations: all.slice(0, 5),
            all_districts: all,
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }

      return new Response("Unhandled", { status: 500 });
    };

    // 1) 진단 생성 → ID 발급 확인
    const created = await createDiagnosis({
      lifeStage: "youth",
      district: "마포구",
      houseType: "officetel",
      areaM2: 30,
      buildingAge: 10,
      floor: 5,
      monthlyIncome: 300,
      deposit: 1000,
      monthlyRent: 80,
    });
    assert.equal(created.id, 1);
    assert.equal(created.monthlyCost, 84.2);
    assert.equal(created.status, "stable");
    assert.equal(STATUS_INFO[created.status].label, "안정");

    // 2) 상세 결과 재조회
    const detail = await getDiagnosis(String(created.id));
    assert.equal(detail.id, 1);
    assert.equal(detail.district, "마포구");
    assert.equal(detail.explanationSource, "basic");

    // 3) 자치구 추천 여정
    const rec = await getRecommendations({
      lifeStage: "youth",
      houseType: "apartment",
      areaM2: 59,
      buildingAge: 10,
      floor: 5,
      monthlyIncome: 400,
    });
    assert.equal(rec.budget, 120);
    assert.equal(rec.all_districts.length, 25);
    assert.equal(rec.recommendations.length, 5);

    // 4) 잘못된 입력(400) 및 미존재 ID(404) 여정
    await assert.rejects(
      () =>
        createDiagnosis({
          lifeStage: "youth",
          district: "마포구",
          houseType: "officetel",
          areaM2: 30,
          buildingAge: 10,
          floor: 5,
          monthlyIncome: 0,
          deposit: 1000,
          monthlyRent: 80,
        }),
      { message: "monthlyIncome: 0보다 커야 합니다" }
    );
    await assert.rejects(() => getDiagnosis("999999"), {
      message: "진단 기록이 없습니다. id=999999",
    });
  } finally {
    globalThis.fetch = originalFetch;
  }
});
