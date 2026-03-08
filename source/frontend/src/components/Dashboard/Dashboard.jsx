import { useState, useEffect, useCallback } from "react";
import { openSensorStream } from "../../api/stateApi.js";
import SensorCard from "./SensorCard.jsx";

export default function Dashboard() {
  // sensor_id → latest MarsEvent
  const [sensors, setSensors] = useState({});
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);

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

  useEffect(() => {
    const es = openSensorStream(handleSnapshot, handleUpdate);

    es.onerror = () => {
      setConnected(false);
      setError("Lost connection to state service — retrying…");
    };

    return () => es.close();
  }, [handleSnapshot, handleUpdate]);

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
