import { useState, useEffect, useCallback } from "react";
import { openMeasurementStream } from "../../api/integrationApi.js";
import SensorCard from "./SensorCard.jsx";

const STREAM_SOURCE_PREFIX = "mars/telemetry/";

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
  Resources: [
    "rest:water_tank_level",
    "rest:hydroponic_ph",
  ],
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
