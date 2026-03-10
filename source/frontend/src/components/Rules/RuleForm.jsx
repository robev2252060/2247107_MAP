import { useState } from "react";

const SENSOR_SOURCES = [
  "greenhouse_temperature", "entrance_humidity", "co2_hall",
  "hydroponic_ph", "water_tank_level", "corridor_pressure",
  "air_quality_pm25", "air_quality_voc",
  "mars/telemetry/solar_array", "mars/telemetry/radiation",
  "mars/telemetry/life_support", "mars/telemetry/thermal_loop",
  "mars/telemetry/power_bus", "mars/telemetry/power_consumption",
  "mars/telemetry/airlock",
];

const ACTUATORS = [
  "cooling_fan", "entrance_humidifier",
  "hall_ventilation", "habitat_heater",
];

const OPERATORS = ["<", "<=", "=", ">=", ">"];

const EMPTY = {
  sensor_source: SENSOR_SOURCES[0],
  sensor_metric: "temperature",
  operator: ">",
  threshold_value: "",
  target_actuator: ACTUATORS[0],
  target_state: "ON",
  description: "",
};

export default function RuleForm({ onSubmit, loading }) {
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState(null);

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (!form.sensor_metric.trim()) {
      setError("Metric is required.");
      return;
    }

    if (!form.threshold_value || isNaN(Number(form.threshold_value))) {
      setError("Threshold value must be a valid number.");
      return;
    }

    try {
      await onSubmit({
        sensor_source: form.sensor_source,
        sensor_metric: form.sensor_metric.trim(),
        operator: form.operator,
        threshold_value: Number(form.threshold_value),
        target_actuator: form.target_actuator,
        target_state: form.target_state,
        enabled: true,
        description: form.description || null,
      });
      setForm(EMPTY);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <form className="rule-form" onSubmit={handleSubmit}>
      <h3 className="rule-form__title">New Rule</h3>

      {error && <div className="rule-form__error">{error}</div>}

      <div className="rule-form__row">
        <label>Sensor Source</label>
        <select name="sensor_source" value={form.sensor_source} onChange={handleChange}>
          {SENSOR_SOURCES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="rule-form__row">
        <label>Metric</label>
        <input
          type="text"
          name="sensor_metric"
          value={form.sensor_metric}
          onChange={handleChange}
          placeholder="e.g. temperature, pm25_ug_m3, voltage_v"
          required
        />
      </div>

      <div className="rule-form__row">
        <label>Operator</label>
        <select name="operator" value={form.operator} onChange={handleChange}>
          {OPERATORS.map((op) => <option key={op} value={op}>{op}</option>)}
        </select>
      </div>

      <div className="rule-form__row">
        <label>Threshold</label>
        <input
          type="number"
          step="any"
          name="threshold_value"
          value={form.threshold_value}
          onChange={handleChange}
          placeholder="e.g. 28"
          required
        />
      </div>

      <div className="rule-form__row">
        <label>Actuator</label>
        <select name="target_actuator" value={form.target_actuator} onChange={handleChange}>
          {ACTUATORS.map((a) => <option key={a} value={a}>{a}</option>)}
        </select>
      </div>

      <div className="rule-form__row">
        <label>Set to</label>
        <select name="target_state" value={form.target_state} onChange={handleChange}>
          <option value="ON">ON</option>
          <option value="OFF">OFF</option>
        </select>
      </div>

      <div className="rule-form__row">
        <label>Description</label>
        <input
          type="text"
          name="description"
          value={form.description}
          onChange={handleChange}
          placeholder="Optional description"
        />
      </div>

      <button className="btn btn--primary" type="submit" disabled={loading}>
        {loading ? "Saving..." : "Add Rule"}
      </button>
    </form>
  );
}
