import { useState } from "react";
import { getRecommendations, type Recommendation } from "../api/api";
import { HOUSE_TYPES, INPUT_STYLE, LIFE_STAGES, STATUS_INFO } from "../components/options";

// 기능 2: 예산에 맞는 자치구 추천
export default function RecommendPage() {
  const [lifeStage, setLifeStage] = useState("youth");
  const [houseType, setHouseType] = useState("apartment");
  const [areaM2, setAreaM2] = useState("59");
  const [buildingAge, setBuildingAge] = useState("10");
  const [floor, setFloor] = useState("5");
  const [monthlyIncome, setMonthlyIncome] = useState("400");

  const [result, setResult] = useState<Recommendation | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    if (Number(monthlyIncome) <= 0) {
      setError("월 소득은 0보다 커야 합니다.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const data = await getRecommendations({
        lifeStage,
        houseType,
        areaM2: Number(areaM2),
        buildingAge: Number(buildingAge),
        floor: Number(floor),
        monthlyIncome: Number(monthlyIncome),
      });
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "추천에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
        <h2 className="text-xl font-bold">자치구 추천</h2>
        <p className="text-sm text-gray-500">원하는 집 조건을 넣으면, 소득의 30% 안에서 살 수 있는 구를 찾아 줍니다.</p>

        <div className="grid grid-cols-2 gap-4">
          <label className="block text-sm">
            생애단계
            <select className={INPUT_STYLE} value={lifeStage} onChange={(e) => setLifeStage(e.target.value)}>
              {LIFE_STAGES.map((item) => (
                <option key={item.value} value={item.value}>{item.label}</option>
              ))}
            </select>
          </label>

          <label className="block text-sm">
            주택 유형
            <select className={INPUT_STYLE} value={houseType} onChange={(e) => setHouseType(e.target.value)}>
              {HOUSE_TYPES.map((item) => (
                <option key={item.value} value={item.value}>{item.label}</option>
              ))}
            </select>
          </label>

          <label className="block text-sm">
            전용면적 (㎡)
            <input className={INPUT_STYLE} type="number" value={areaM2} onChange={(e) => setAreaM2(e.target.value)} />
          </label>

          <label className="block text-sm">
            건물 나이 (년)
            <input className={INPUT_STYLE} type="number" value={buildingAge} onChange={(e) => setBuildingAge(e.target.value)} />
          </label>

          <label className="block text-sm">
            층
            <input className={INPUT_STYLE} type="number" value={floor} onChange={(e) => setFloor(e.target.value)} />
          </label>

          <label className="block text-sm">
            월 소득 (만원)
            <input className={INPUT_STYLE} type="number" value={monthlyIncome} onChange={(e) => setMonthlyIncome(e.target.value)} />
          </label>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full py-3 rounded-xl bg-emerald-700 text-white font-bold disabled:opacity-50"
        >
          {loading ? "25개 구를 계산하는 중..." : "추천 받기"}
        </button>
      </div>

      {result && (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <p className="font-bold mb-1">월 예산 {result.budget}만원 (소득의 30%)</p>
          <p className="text-sm text-gray-500 mb-4">예산 안에 드는 구: {result.within_budget_count}곳 / 25곳</p>

          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="py-2">구</th>
                <th>예상 주거비</th>
                <th>소득 대비</th>
                <th>단계</th>
              </tr>
            </thead>
            <tbody>
              {result.all_districts.map((item) => {
                const status = STATUS_INFO[item.status] ?? STATUS_INFO.unknown;
                return (
                  <tr key={item.district} className="border-b last:border-0">
                    <td className="py-2 font-medium">{item.district}</td>
                    <td>{item.predicted_cost}만원</td>
                    <td>{item.rir_percent}%</td>
                    <td>
                      <span className={`px-2 py-0.5 rounded-full text-xs ${status.color}`}>{status.label}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
