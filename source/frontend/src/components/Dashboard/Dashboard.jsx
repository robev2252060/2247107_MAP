import { useState, useEffect, useCallback, useMemo } from "react";
import { openMeasurementStream } from "../../api/integrationApi.js";
import SensorCard from "./SensorCard.jsx";
import SensorLineChart from "./SensorLineChart.jsx";

const STREAM_SOURCE_PREFIX = "mars/telemetry/";

function humanizeSensorKey(key) {
  if (!key || typeof key !== "string") return "";

  // Example: rest:co2_hall -> CO2 Hall
  // Example: stream:mars/telemetry/power_bus -> Power Bus
  const parts = key.split(":");
  if (parts.length === 2 && parts[0] === "rest") {
    return parts[1].replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  }

  if (parts.length === 2 && parts[0] === "stream") {
    const name = parts[1].replace(STREAM_SOURCE_PREFIX, "");
    return name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  }

  return key;
}

const SENSOR_GROUPS = {
  Thermal: [
    "rest:greenhouse_temperature",
    "stream:mars/telemetry/thermal_loop",
  ],
  Power: [
    "stream:mars/telemetry/power_bus",
    "stream:mars/telemetry/power_consumption",
    "stream:mars/telemetry/solar_array",
  ],
  "Air Quality": [
    "rest:co2_hall",
    "rest:air_quality_voc",
    "rest:air_quality_pm25",
  ],
  Environment: [
    "rest:entrance_humidity",
    "rest:corridor_pressure",
    "stream:mars/telemetry/radiation",
  ],
  Resources: ["rest:water_tank_level", "rest:hydroponic_ph"],
  Operations: [
    "stream:mars/telemetry/airlock",
    "stream:mars/telemetry/life_support",
  ],
};

const SENSOR_GROUP_ICONS = {
  Thermal: "🌡️",
  Power: "⚡",
  "Air Quality": "💨",
  Environment: "🌍",
  Resources: "💧",
  Operations: "🚪",
};

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
  const [history, setHistory] = useState({});
  const [selectedSensorKey, setSelectedSensorKey] = useState(
    "rest:greenhouse_temperature",
  );

  const handleMeasurement = useCallback((event) => {
    const key = toSensorKey(event?.source);

    setSensors((prev) => ({
      ...prev,
      [key]: event,
    }));

    // Capture the first numeric reading for charting
    const reading = (event?.readings || []).find(
      (r) => typeof r.value === "number",
    );
    if (reading) {
      setHistory((prev) => {
        const existing = prev[key] || [];
        const next = [
          ...existing,
          {
            time: new Date(event.timestamp || Date.now()),
            value: reading.value,
          },
        ];
        return { ...prev, [key]: next.slice(-60) };
      });
    }

    setConnected(true);
    setError(null);
  }, []);

  useEffect(() => {
    const es = openMeasurementStream(handleMeasurement);

    es.onerror = () => {
      setConnected(false);
      setError("Lost connection to integration service - retrying...");
    };

    return () => es.close();
  }, [handleMeasurement]);

  const availableChartSensors = useMemo(() => {
    // only show REST-based sensors since those are polled
    return Object.values(SENSOR_GROUPS)
      .flat()
      .filter((key) => key.startsWith("rest:"));
  }, []);

  if (error && !connected) {
    return <div className="error-banner">{error}</div>;
  }

  const hasData = Object.keys(sensors).length > 0;

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

      <div style={{ marginBottom: "1.5rem" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "1rem",
            flexWrap: "wrap",
          }}
        >
          <label style={{ color: "var(--color-muted)", fontSize: "0.85rem" }}>
            Chart sensor:
            <select
              value={selectedSensorKey || ""}
              onChange={(e) => setSelectedSensorKey(e.target.value)}
              style={{
                marginLeft: "0.5rem",
                padding: "0.25rem 0.5rem",
                borderRadius: "4px",
                border: "1px solid var(--color-border)",
                background: "var(--color-bg)",
                color: "var(--color-text)",
              }}
            >
              <option value="">(select sensor)</option>
              {availableChartSensors.map((key) => (
                <option key={key} value={key}>
                  {humanizeSensorKey(key)}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div style={{ marginTop: "1rem" }}>
          <SensorLineChart
            sensorKey={selectedSensorKey}
            data={history[selectedSensorKey]}
          />
        </div>
      </div>

      {!hasData ? (
        <p className="dashboard__empty">Waiting for sensor data...</p>
      ) : (
        <>
          {Object.entries(SENSOR_GROUPS).map(([groupName, keys]) => {
            const groupHasData = keys.some((key) => sensors[key]);
            if (!groupHasData) return null;

            return (
              <div className="sensor-group" key={groupName}>
                <h2 className="sensor-group__title">
                  {SENSOR_GROUP_ICONS[groupName] ?? ""} {groupName}
                </h2>
                <div className="sensor-group__cards">
                  {keys.map((sensorKey) => (
                    <SensorCard
                      key={sensorKey}
                      sensorKey={sensorKey}
                      event={sensors[sensorKey]}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </>
      )}
    </section>
  );
}
