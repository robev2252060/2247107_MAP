import { useState, useEffect, useCallback } from "react";
import { fetchActuators, openActuatorStream, setActuatorState } from "../api/actuatorApi.js";
import ActuatorPanel from "../components/Actuators/ActuatorPanel.jsx";

function nowIso() {
  return new Date().toISOString();
}

function applyMeasurement(prev, event) {
  const actuatorId = event?.source;
  const stateReading = (event?.readings || []).find((r) => r.metric === "state");
  const newState = stateReading?.value;
  const updatedAt = event?.timestamp || nowIso();

  if (!actuatorId || (newState !== "ON" && newState !== "OFF")) {
    return prev;
  }

  const idx = prev.findIndex((a) => a.actuator_name === actuatorId);
  if (idx === -1) {
    return [...prev, { actuator_name: actuatorId, state: newState, updated_at: updatedAt }];
  }

  return prev.map((a) =>
    a.actuator_name === actuatorId
      ? { ...a, state: newState, updated_at: updatedAt }
      : a
  );
}

export default function ActuatorsPage() {
  const [actuators, setActuators] = useState([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const loadActuators = useCallback(async () => {
    try {
      setError(null);
      const data = await fetchActuators();
      setActuators(data.map((a) => ({ ...a, updated_at: a.updated_at || nowIso() })));
      setLastRefreshed(new Date());
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    loadActuators();

    const es = openActuatorStream((event) => {
      setActuators((prev) => applyMeasurement(prev, event));
      setError(null);
    });

    es.onopen = () => {
      setConnected(true);
      setError(null);
    };

    es.onerror = () => {
      setConnected(false);
      setError("Lost actuator stream connection - retrying...");
    };

    return () => es.close();
  }, [loadActuators]);

  async function handleRefresh() {
    setRefreshing(true);
    try {
      await loadActuators();
    } finally {
      setRefreshing(false);
    }
  }

  async function handleToggle(actuatorId, newState) {
    try {
      await setActuatorState(actuatorId, newState);
      const updatedAt = nowIso();
      setActuators((prev) =>
        prev.map((a) =>
          a.actuator_name === actuatorId ? { ...a, state: newState, updated_at: updatedAt } : a
        )
      );
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="page">
      <div className="dashboard__header">
        <div style={{ display: "flex", gap: "1rem", alignItems: "flex-end" }}>
          <div>
            <h1>Actuator Control</h1>
            {lastRefreshed ? (
              <div style={{ fontSize: "0.85rem", color: "var(--color-muted)" }}>
                Last refreshed: {lastRefreshed.toLocaleTimeString()}
              </div>
            ) : (
              <div style={{ fontSize: "0.85rem", color: "var(--color-muted)" }}>
                Loading actuator state…
              </div>
            )}
          </div>

          <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
            <button
              className="btn btn--ghost btn--sm"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              {refreshing ? "Refreshing…" : "Refresh"}
            </button>

            <span className={`status-dot ${connected ? "status-dot--ok" : "status-dot--err"}`}>
              {connected ? "● Live" : "○ Connecting..."}
            </span>
          </div>
        </div>
      </div>
      {error && <div className="error-banner">{error}</div>}
      <ActuatorPanel actuators={actuators} onToggle={handleToggle} />
    </section>
  );
}
