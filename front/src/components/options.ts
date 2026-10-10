// 선택 상자(select)에 보여 줄 목록. 여러 화면에서 같이 쓴다.

export const LIFE_STAGES = [
  { value: "youth", label: "청년" },
  { value: "family", label: "신혼·육아 가구" },
  { value: "senior", label: "중장년·노년" },
];

export const HOUSE_TYPES = [
  { value: "apartment", label: "아파트" },
  { value: "officetel", label: "오피스텔" },
  { value: "house", label: "단독/다가구" },
  { value: "villa", label: "연립/다세대" },
];

export const DISTRICTS = [
  "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구",
  "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구",
  "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구",
];

// 위험 단계 이름과 색
export const STATUS_INFO: Record<string, { label: string; color: string }> = {
  stable: { label: "안정", color: "bg-emerald-100 text-emerald-800" },
  warning: { label: "주의", color: "bg-amber-100 text-amber-800" },
  danger: { label: "위험 (Red Zone)", color: "bg-red-100 text-red-800" },
  unknown: { label: "판단 불가", color: "bg-gray-100 text-gray-700" },
};

// 입력칸에 공통으로 쓰는 스타일
export const INPUT_STYLE =
  "w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-600";
