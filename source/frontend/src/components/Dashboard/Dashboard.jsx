import { useState, useEffect, useCallback } from "react";
import { openSensorStream } from "../../api/stateApi.js";
import SensorCard from "./SensorCard.jsx";
import { useToast } from "../Toast/ToastContainer.jsx";

export default function Dashboard() {
  // sensor_id → latest MarsEvent
  const [sensors, setSensors] = useState({});
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const addToast = useToast();

  const handleSnapshot = useCallback((snapshot) => {
    setSensors(snapshot);
    setConnected(true);
  }, []);

  const handleUpdate = useCallback((event) => {
    setSensors((prev) => ({
      ...prev,
      [event.sensor_id]: event,
    }));
  }, []);

  const handleRuleEvent = useCallback((event) => {
    const sensor = event.sensor_id?.replace(/_/g, " ");
    const actuator = event.actuator_id?.replace(/_/g, " ");
    const desc = event.description ? ` (${event.description})` : "";
    if (event.triggered) {
      addToast(
        `Rule triggered${desc}: ${sensor} ${event.operator} ${event.threshold}${event.unit ? ` ${event.unit}` : ""} → ${actuator} ${event.actuator_state}`,
        "success",
      );
    } else {
      addToast(
        `Rule cleared${desc}: ${sensor} ${event.operator} ${event.threshold}${event.unit ? ` ${event.unit}` : ""} → ${actuator} no longer active`,
        "info",
      );
    }
  }, [addToast]);

  useEffect(() => {
    const es = openSensorStream(handleSnapshot, handleUpdate, handleRuleEvent);

    es.onerror = () => {
      setConnected(false);
      setError("Lost connection to state service — retrying…");
    };

    return () => es.close();
  }, [handleSnapshot, handleUpdate, handleRuleEvent]);

  if (error && !connected) {
    return <div className="error-banner">{error}</div>;
  }

  const entries = Object.entries(sensors);

  return (
    <section className="dashboard">
      <div className="dashboard__header">
        <h1>Live Sensor Dashboard</h1>
        <span className={`status-dot ${connected ? "status-dot--ok" : "status-dot--err"}`}>
          {connected ? "● Live" : "○ Connecting…"}
        </span>
      </div>

      {entries.length === 0 ? (
        <p className="dashboard__empty">Waiting for sensor data…</p>
      ) : (
        <div className="sensor-grid">
          {entries.map(([sensorId, event]) => (
            <SensorCard key={sensorId} sensorId={sensorId} event={event} />
          ))}
        </div>
      )}
    </section>
  );
}
