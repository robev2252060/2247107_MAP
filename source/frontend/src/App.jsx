import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout/Layout.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import RulesPage from "./pages/RulesPage.jsx";
import ActuatorsPage from "./pages/ActuatorsPage.jsx";
import SettingsPage from "./pages/SettingsPage.jsx";
import { ToastProvider, useToast } from "./components/Toast/ToastContainer.jsx";
import { openActuatorStream } from "./api/actuatorApi.js";

function RuleNotificationsListener() {
  const addToast = useToast();

  useEffect(() => {
    const es = openActuatorStream((event) => {
      if (event?.rule_id) {
        const actuatorId = event?.source;
        const stateReading = (event?.readings || []).find((r) => r.metric === "state");
        const newState = stateReading?.value;
        addToast(`Rule Activated: ${actuatorId} set to ${newState}`, "info");
      }
    });

    return () => es.close();
  }, [addToast]);

  return null;
}

export default function App() {
  return (
    <ToastProvider>
      <RuleNotificationsListener />
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/rules" element={<RulesPage />} />
            <Route path="/actuators" element={<ActuatorsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ToastProvider>
  );
}
