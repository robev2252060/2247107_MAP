/**
 * SensorCard
 * Displays the latest MeasurementEvent for a single source.
 */

const SENSOR_ICONS = {
  "rest:greenhouse_temperature": "🌡️",
  "rest:entrance_humidity": "💧",
  "rest:co2_hall": "🫁",
  "rest:hydroponic_ph": "🧪",
  "rest:water_tank_level": "🪣",
  "rest:corridor_pressure": "🌬️",
  "rest:air_quality_pm25": "🌫️",
  "rest:air_quality_voc": "⚗️",
  "stream:mars/telemetry/solar_array": "🔋",
  "stream:mars/telemetry/radiation": "☢️",
  "stream:mars/telemetry/life_support": "🌱",
  "stream:mars/telemetry/thermal_loop": "♨️",
  "stream:mars/telemetry/power_bus": "⚡",
  "stream:mars/telemetry/power_consumption": "🔌",
  "stream:mars/telemetry/airlock": "🚪",
};

function formatLabel(sensorKey, source) {
  const raw = source || sensorKey.replace(/^(rest:|stream:)/, "");
  return raw.replace(/^mars\/telemetry\//, "").replace(/_/g, " ");
}

function formatValue(value, unit) {
  if (value === null || value === undefined) return "-";
  const normalized = typeof value === "number" ? value.toFixed(2) : String(value);
  return unit ? `${normalized} ${unit}` : normalized;
}

export default function SensorCard({ sensorKey, event }) {
  const icon = SENSOR_ICONS[sensorKey] ?? "📡";
  const label = formatLabel(sensorKey, event?.source);
  const ts = event?.timestamp ? new Date(event.timestamp).toLocaleTimeString() : "-";
  const readings = Array.isArray(event?.readings) ? event.readings : [];

  return (
    <div className="sensor-card">
      <div className="sensor-card__icon">{icon}</div>
      <div className="sensor-card__body">
        <span className="sensor-card__label">{label}</span>
        <div className="sensor-card__metrics">
          {readings.map((reading) => (
            <div className="sensor-card__metric" key={reading.metric}>
              <span className="sensor-card__metric-name">{reading.metric}</span>
              <span className="sensor-card__metric-value">{formatValue(reading.value, reading.unit)}</span>
            </div>
          ))}
        </div>
        <span className="sensor-card__ts">Updated {ts}</span>
      </div>
    </div>
  );
}
