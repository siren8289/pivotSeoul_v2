import { Link, Route, Routes } from "react-router-dom";
import DiagnosePage from "./pages/DiagnosePage";
import RecommendPage from "./pages/RecommendPage";
import ResultPage from "./pages/ResultPage";

// 화면 뼈대: 위쪽 메뉴 + 주소(URL)에 따라 바뀌는 본문
export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-slate-800">
      <header className="bg-white border-b border-gray-200 h-16 flex items-center px-6">
        <div className="w-full max-w-3xl mx-auto flex items-center gap-6">
          <span className="font-bold text-xl text-emerald-700">pivotSeoul</span>
          <Link to="/" className="text-sm hover:text-emerald-700">내 주거비 진단</Link>
          <Link to="/recommend" className="text-sm hover:text-emerald-700">자치구 추천</Link>
        </div>
      </header>

      <main className="max-w-3xl mx-auto p-6">
        <Routes>
          <Route path="/" element={<DiagnosePage />} />
          <Route path="/recommend" element={<RecommendPage />} />
          <Route path="/diagnoses/:id" element={<ResultPage />} />
        </Routes>
      </main>
    </div>
  );
}
