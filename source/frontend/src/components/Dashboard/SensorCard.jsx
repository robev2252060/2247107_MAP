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

const METRIC_LABELS = {
  co2_ppm: "CO₂",
  pm1_ug_m3: "PM1",
  pm25_ug_m3: "PM2.5",
  pm10_ug_m3: "PM10",
  level_pct: "Level",
  level_liters: "Level (L)",
  power_kw: "Power",
  voltage_v: "Voltage",
  current_a: "Current",
  cumulative_kwh: "Energy",
  temperature_c: "Temperature",
  flow_l_min: "Flow",
  cycles_per_hour: "Cycles/hr",
};

const SENSOR_TITLES = {
  "rest:greenhouse_temperature": "Greenhouse Temperature",
  "rest:entrance_humidity": "Entrance Humidity",
  "rest:co2_hall": "CO₂ Hall",
  "rest:hydroponic_ph": "Hydroponic pH",
  "rest:water_tank_level": "Water Tank Level",
  "rest:corridor_pressure": "Corridor Pressure",
  "rest:air_quality_pm25": "Air Quality PM2.5",
  "rest:air_quality_voc": "Air Quality VOC",
  "stream:mars/telemetry/solar_array": "Solar Array",
  "stream:mars/telemetry/radiation": "Radiation",
  "stream:mars/telemetry/life_support": "Life Support",
  "stream:mars/telemetry/thermal_loop": "Thermal Loop",
  "stream:mars/telemetry/power_bus": "Power Bus",
  "stream:mars/telemetry/power_consumption": "Power Consumption",
  "stream:mars/telemetry/airlock": "Airlock",
};

function formatLabel(sensorKey) {
  return (
    SENSOR_TITLES[sensorKey] ??
    sensorKey
      .replace(/^(rest:|stream:|mars\/telemetry\/)/, "")
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase())
  );
}


function formatMetricName(metric, unit) {
  if (!metric) return "";
  if (METRIC_LABELS[metric]) return METRIC_LABELS[metric];

  // Fallback: remove unit suffix patterns like _ppm, _ug_m3, _c, _v, _a
  return metric
    .replace(/_ppm$/, "")
    .replace(/_ug_m3$/, "")
    .replace(/_ug_m³$/, "")
    .replace(/_c$/, "")
    .replace(/_v$/, "")
    .replace(/_a$/, "")
    .replace(/_/g, " ")
    .replace(/\b([a-z])/, (m) => m.toUpperCase());
}

function formatValue(value, unit) {
  if (value === null || value === undefined) return "-";
  const normalized =
    typeof value === "number" ? value.toFixed(2) : String(value);
  return unit ? `${normalized} ${unit}` : normalized;
}

function isStale(timestamp) {
  if (!timestamp) return true;
  const FIVE_MINUTES = 5 * 60 * 1000;
  return Date.now() - new Date(timestamp).getTime() > FIVE_MINUTES;
}

export default function SensorCard({ sensorKey, event }) {
  const icon = SENSOR_ICONS[sensorKey] ?? "📡";
  const label = formatLabel(sensorKey);
  const ts = event?.timestamp
    ? new Date(event.timestamp).toLocaleTimeString()
    : "-";
  const readings = Array.isArray(event?.readings) ? event.readings : [];
  const stale = isStale(event?.timestamp);

  return (
    <div className={`sensor-card ${stale ? "sensor-card--stale" : ""}`}>
      <div className="sensor-card__icon">{icon}</div>
      <div className="sensor-card__body">
        <span className="sensor-card__label">{label}</span>
        <div className="sensor-card__metrics">
          {readings.map((reading) => (
            <div className="sensor-card__metric" key={reading.metric}>
              <span className="sensor-card__metric-name">
                {formatMetricName(reading.metric, reading.unit)}
              </span>
              <span className="sensor-card__metric-value">
                {formatValue(reading.value, reading.unit)}
              </span>
            </div>
          ))}
        </div>
        <span className="sensor-card__ts">
          Updated {ts}
          {stale && (
            <span className="sensor-card__stale-badge">⚠️ Stale data</span>
          )}
        </span>
      </div>
    </div>
  );
}
