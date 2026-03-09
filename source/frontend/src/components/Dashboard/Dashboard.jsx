import { useState, useEffect, useCallback } from "react";
import { openMeasurementStream } from "../../api/integrationApi.js";
import SensorCard from "./SensorCard.jsx";

const STREAM_SOURCE_PREFIX = "mars/telemetry/";

function toSensorKey(source) {
  if (!source) return "unknown:unknown";
  if (source.startsWith(STREAM_SOURCE_PREFIX)) {
    return `stream:${source}`;
  }
  return `rest:${source}`;
}

export default function Dashboard() {
  const [sensors, setSensors] = useState({});
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);

  const handleMeasurement = useCallback(
    (event) => {
      const key = toSensorKey(event?.source);

      setSensors((prev) => ({
        ...prev,
        [key]: event,
      }));

      setConnected(true);
      setError(null);
    },
    [],
  );

  useEffect(() => {
    const es = openMeasurementStream(handleMeasurement);

    es.onerror = () => {
      setConnected(false);
      setError("Lost connection to integration service - retrying...");
    };

    return () => es.close();
  }, [handleMeasurement]);

  if (error && !connected) {
    return <div className="error-banner">{error}</div>;
  }

  const entries = Object.entries(sensors);

  return (
    <section className="dashboard">
      <div className="dashboard__header">
        <h1>Live Sensor Dashboard</h1>
        <span
          className={`status-dot ${
            connected ? "status-dot--ok" : "status-dot--err"
          }`}
        >
          {connected ? "● Live" : "○ Connecting..."}
        </span>
      </div>

      {entries.length === 0 ? (
        <p className="dashboard__empty">Waiting for sensor data...</p>
      ) : (
        <div className="sensor-grid">
          {entries.map(([sensorKey, event]) => (
            <SensorCard key={sensorKey} sensorKey={sensorKey} event={event} />
          ))}
        </div>
      )}
    </section>
  );
}
