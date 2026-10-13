import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createDiagnosis } from "../api/api";
import { DISTRICTS, HOUSE_TYPES, INPUT_STYLE, LIFE_STAGES } from "../components/options";

// 기능 1: 내 주거비 진단 입력 화면
export default function DiagnosePage() {
  const navigate = useNavigate();

  // 입력값은 모두 state(화면이 기억하는 값)로 관리한다. 숫자 칸도 입력 중에는 글자로 둔다.
  const [lifeStage, setLifeStage] = useState("youth");
  const [district, setDistrict] = useState("마포구");
  const [houseType, setHouseType] = useState("apartment");
  const [areaM2, setAreaM2] = useState("59");
  const [buildingAge, setBuildingAge] = useState("10");
  const [floor, setFloor] = useState("5");
  const [monthlyIncome, setMonthlyIncome] = useState("300");
  const [deposit, setDeposit] = useState("5000");
  const [monthlyRent, setMonthlyRent] = useState("80");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // "진단하기" 버튼을 눌렀을 때 실행된다.
  async function handleSubmit() {
    if (Number(monthlyIncome) <= 0) {
      setError("월 소득은 0보다 커야 합니다.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const result = await createDiagnosis({
        lifeStage,
        district,
        houseType,
        areaM2: Number(areaM2),
        buildingAge: Number(buildingAge),
        floor: Number(floor),
        monthlyIncome: Number(monthlyIncome),
        deposit: Number(deposit),
        monthlyRent: Number(monthlyRent),
      });
      // 성공하면 결과 화면으로 이동
      navigate(`/diagnoses/${result.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "진단에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
      <h2 className="text-xl font-bold">내 주거비 진단</h2>
      <p className="text-sm text-gray-500">금액은 모두 만원 단위입니다. 전세는 월세를 0으로 입력하세요.</p>

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
          자치구
          <select className={INPUT_STYLE} value={district} onChange={(e) => setDistrict(e.target.value)}>
            {DISTRICTS.map((name) => (
              <option key={name} value={name}>{name}</option>
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

        <label className="block text-sm">
          보증금 (만원)
          <input className={INPUT_STYLE} type="number" value={deposit} onChange={(e) => setDeposit(e.target.value)} />
        </label>

        <label className="block text-sm">
          월세 (만원)
          <input className={INPUT_STYLE} type="number" value={monthlyRent} onChange={(e) => setMonthlyRent(e.target.value)} />
        </label>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        onClick={handleSubmit}
        disabled={loading}
        className="w-full py-3 rounded-xl bg-emerald-700 text-white font-bold disabled:opacity-50 cursor-pointer transition hover:bg-emerald-800"
      >
        {loading ? "진단 분석 중..." : "진단하기"}
      </button>
    </div>
  );
}
