import assert from "node:assert/strict";
import test from "node:test";
import {
  DISTRICTS,
  HOUSE_TYPES,
  INPUT_STYLE,
  LIFE_STAGES,
  STATUS_INFO,
} from "../src/components/options.ts";
import {
  createDiagnosis,
  getDiagnosis,
  getRecommendations,
} from "../src/api/api.ts";

test("options.ts: 25개 서울 자치구·생애단계·주택유형·상태 배지 정합성", () => {
  assert.equal(DISTRICTS.length, 25);
  assert.equal(new Set(DISTRICTS).size, 25);
  assert.ok(DISTRICTS.includes("마포구"));
  assert.ok(DISTRICTS.includes("강남구"));

  assert.deepEqual(
    LIFE_STAGES.map((item) => item.value),
    ["youth", "family", "senior"]
  );
  assert.deepEqual(
    HOUSE_TYPES.map((item) => item.value),
    ["apartment", "officetel", "house", "villa"]
  );
  assert.deepEqual(Object.keys(STATUS_INFO), [
    "stable",
    "warning",
    "danger",
    "unknown",
  ]);
  assert.ok(INPUT_STYLE.includes("rounded-lg"));
});

test("api.ts: createDiagnosis·getDiagnosis·getRecommendations 정상 및 오류 처리", async () => {
  const originalFetch = globalThis.fetch;
  try {
    const calls = [];
    globalThis.fetch = async (url, options = {}) => {
      calls.push({ url: String(url), options });
      if (String(url).endsWith("/api/diagnoses") && options.method === "POST") {
        return new Response(
          JSON.stringify({
            id: 7,
            district: "마포구",
            monthlyCost: 84.2,
            rirPercent: 28.1,
            status: "stable",
            redZone: false,
            mlPrice: 90,
            dlPrice: 88,
            marketPrice: 89,
            priceGapPercent: -5.4,
            districtMedianCost: 95,
            auditCount: 101,
            explanation: "안정 단계입니다.",
            explanationSource: "basic",
          }),
          { status: 201, headers: { "Content-Type": "application/json" } }
        );
      }
      if (String(url).endsWith("/api/diagnoses/7")) {
        return new Response(
          JSON.stringify({ id: 7, district: "마포구", status: "stable" }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      if (String(url).endsWith("/api/diagnoses/999")) {
        return new Response(
          JSON.stringify({
            errorCode: "NOT_FOUND",
            message: "진단 기록이 없습니다. id=999",
          }),
          { status: 404, headers: { "Content-Type": "application/json" } }
        );
      }
      if (String(url).endsWith("/api/recommendations")) {
        return new Response(
          JSON.stringify({
            budget: 120,
            within_budget_count: 10,
            recommendations: [],
            all_districts: [],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      return new Response("Not Found", { status: 500 });
    };

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
    assert.equal(created.id, 7);
    assert.equal(created.status, "stable");

    const fetched = await getDiagnosis("7");
    assert.equal(fetched.district, "마포구");

    const rec = await getRecommendations({
      lifeStage: "youth",
      houseType: "apartment",
      areaM2: 59,
      buildingAge: 10,
      floor: 5,
      monthlyIncome: 400,
    });
    assert.equal(rec.budget, 120);

    await assert.rejects(() => getDiagnosis("999"), {
      message: "진단 기록이 없습니다. id=999",
    });
    assert.equal(calls.length, 4);
  } finally {
    globalThis.fetch = originalFetch;
  }
});
