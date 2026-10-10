// Spring 서버와 통신하는 함수를 한 곳에 모았다.

// 서버 주소. .env 의 VITE_API_URL 이 없으면 로컬 주소를 쓴다.
const API_URL: string = import.meta.env.VITE_API_URL ?? "http://localhost:8080";

// ---------- 타입(데이터 모양) ----------

// 진단 요청. 금액은 모두 만원 단위
export type DiagnoseInput = {
  lifeStage: string;
  district: string;
  houseType: string;
  areaM2: number;
  buildingAge: number;
  floor: number;
  monthlyIncome: number;
  deposit: number;
  monthlyRent: number;
};

// 진단 결과
export type Diagnosis = DiagnoseInput & {
  id: number;
  monthlyCost: number;          // 월 환산 주거비
  rirPercent: number | null;    // 소득 대비 주거비 비율(%)
  status: string;               // stable / warning / danger
  redZone: boolean;
  mlPrice: number;              // ML 예측 시세
  dlPrice: number;              // DL 예측 시세
  marketPrice: number;          // 두 모델 평균
  priceGapPercent: number;      // 시세 대비 차이(%)
  districtMedianCost: number | null;
  jeonseRatio: number | null;
  explanation: string;          // LLM 설명
  explanationSource: string;    // gemini / basic
};

// 추천 요청
export type RecommendInput = {
  lifeStage: string;
  houseType: string;
  areaM2: number;
  buildingAge: number;
  floor: number;
  monthlyIncome: number;
};

// 추천 결과의 구 1개
export type DistrictItem = {
  district: string;
  predicted_cost: number;
  rir_percent: number | null;
  status: string;
  is_red_zone: boolean;
  within_budget: boolean;
  deal_count: number | null;
  jeonse_ratio: number | null;
};

export type Recommendation = {
  budget: number;
  within_budget_count: number;
  recommendations: DistrictItem[];
  all_districts: DistrictItem[];
};

// ---------- 공통 요청 함수 ----------

// 서버에 요청을 보내고 JSON 결과를 돌려준다. 실패하면 오류 메시지를 던진다.
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(API_URL + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    // Spring 오류는 { errorCode, message } 모양이다.
    let message = "요청에 실패했습니다.";
    try {
      const body = await response.json();
      message = body.message ?? message;
    } catch {
      // JSON이 아니면 기본 문장을 쓴다.
    }
    throw new Error(message);
  }
  return response.json();
}

// ---------- 서버 호출 ----------

export function createDiagnosis(input: DiagnoseInput) {
  return request<Diagnosis>("/api/diagnoses", { method: "POST", body: JSON.stringify(input) });
}

export function getDiagnosis(id: string) {
  return request<Diagnosis>(`/api/diagnoses/${id}`);
}

export function getRecommendations(input: RecommendInput) {
  return request<Recommendation>("/api/recommendations", { method: "POST", body: JSON.stringify(input) });
}
