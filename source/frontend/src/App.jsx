import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout/Layout.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import RulesPage from "./pages/RulesPage.jsx";
import ActuatorsPage from "./pages/ActuatorsPage.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/rules" element={<RulesPage />} />
          <Route path="/actuators" element={<ActuatorsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
