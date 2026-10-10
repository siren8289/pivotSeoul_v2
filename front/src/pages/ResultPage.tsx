import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getDiagnosis, type Diagnosis } from "../api/api";
import { STATUS_INFO } from "../components/options";

// 기능 1: 진단 결과 화면 (주소의 id로 결과를 불러온다)
export default function ResultPage() {
  const { id } = useParams();
  const [result, setResult] = useState<Diagnosis | null>(null);
  const [error, setError] = useState("");

  // 화면이 처음 나타날 때 한 번 결과를 불러온다.
  useEffect(() => {
    if (!id) return;
    getDiagnosis(id)
      .then(setResult)
      .catch((e) => setError(e instanceof Error ? e.message : "결과를 불러오지 못했습니다."));
  }, [id]);

  if (error) return <p className="text-red-600">{error}</p>;
  if (!result) return <p className="text-gray-500">불러오는 중...</p>;

  const status = STATUS_INFO[result.status] ?? STATUS_INFO.unknown;
  const gap = result.priceGapPercent;
  // 시세보다 얼마나 비싼지/싼지 문장으로 바꾼다.
  const gapText = gap > 0 ? `시세보다 ${gap}% 비쌉니다` : `시세보다 ${Math.abs(gap)}% 쌉니다`;

  return (
    <div className="space-y-4">
      {/* 1) 규칙 계산: RIR */}
      <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <p className="text-sm text-gray-500">{result.district} · 월 환산 주거비 {result.monthlyCost}만원</p>
        <p className="text-4xl font-bold my-2">소득의 {result.rirPercent}%</p>
        <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${status.color}`}>
          {status.label}
        </span>
        <p className="text-xs text-gray-400 mt-3">
          월 환산 주거비 = 월세 + 보증금 × 5% ÷ 12 / 소득 대비 40% 초과면 Red Zone
        </p>
      </section>

      {/* 2) ML · DL: 예상 시세 비교 */}
      <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <h3 className="font-bold mb-3">AI 예상 시세 (월 환산, 만원)</h3>
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="bg-gray-50 rounded-xl p-3">
            <p className="text-xs text-gray-500">ML (랜덤포레스트)</p>
            <p className="text-xl font-bold">{result.mlPrice}</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-3">
            <p className="text-xs text-gray-500">DL (신경망)</p>
            <p className="text-xl font-bold">{result.dlPrice}</p>
          </div>
          <div className="bg-emerald-50 rounded-xl p-3">
            <p className="text-xs text-gray-500">평균</p>
            <p className="text-xl font-bold">{result.marketPrice}</p>
          </div>
        </div>
        <p className="mt-3 text-sm">내 주거비는 {gapText}.</p>
        {result.districtMedianCost !== null && (
          <p className="text-sm text-gray-500">{result.district} 같은 유형 실거래 중앙값: {result.districtMedianCost}만원</p>
        )}
        {result.jeonseRatio !== null && (
          <p className="text-sm text-gray-500">{result.district} 아파트 전세가율: {Math.round(result.jeonseRatio * 100)}%</p>
        )}
      </section>

      {/* 3) LLM: 쉬운 설명 */}
      <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <h3 className="font-bold mb-2">
          AI 설명 <span className="text-xs font-normal text-gray-400">({result.explanationSource === "gemini" ? "Gemini" : "기본 문장"})</span>
        </h3>
        <p className="text-sm leading-relaxed whitespace-pre-line">{result.explanation}</p>
      </section>

      <Link to="/" className="block text-center text-sm text-emerald-700">← 다시 진단하기</Link>
    </div>
  );
}
