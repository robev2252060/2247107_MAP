/**
 * SensorCard
 * Displays the latest reading for a single sensor.
 * Highlights briefly when the value updates (CSS animation triggered by key).
 */

const SENSOR_ICONS = {
  greenhouse_temperature: "🌡️",
  entrance_humidity:       "💧",
  co2_hall:                "🫁",
  hydroponic_ph:           "🧪",
  water_tank_level:        "🪣",
  corridor_pressure:       "🌬️",
  air_quality_pm25:        "🌫️",
  air_quality_voc:         "⚗️",
};

function formatValue(value, unit) {
  if (value === null || value === undefined) return "—";
  const num = typeof value === "number" ? value.toFixed(2) : value;
  return unit ? `${num} ${unit}` : String(num);
}

export default function SensorCard({ sensorId, event }) {
  const icon = SENSOR_ICONS[sensorId] ?? "📡";
  const label = sensorId.replace(/_/g, " ");
  const displayValue = formatValue(event?.value, event?.unit);
  const ts = event?.timestamp
    ? new Date(event.timestamp).toLocaleTimeString()
    : "—";

  return (
    <div className="sensor-card" key={event?.event_id}>
      <div className="sensor-card__icon">{icon}</div>
      <div className="sensor-card__body">
        <span className="sensor-card__label">{label}</span>
        <span className="sensor-card__value">{displayValue}</span>
        <span className="sensor-card__ts">Updated {ts}</span>
      </div>
    </div>
  );
}
