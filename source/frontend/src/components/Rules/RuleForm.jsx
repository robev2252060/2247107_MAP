import { useState } from "react";

const SENSORS = [
  "greenhouse_temperature", "entrance_humidity", "co2_hall",
  "hydroponic_ph", "water_tank_level", "corridor_pressure",
  "air_quality_pm25", "air_quality_voc",
];

const ACTUATORS = [
  "cooling_fan", "entrance_humidifier",
  "hall_ventilation", "habitat_heater",
];

const OPERATORS = ["<", "<=", "=", ">=", ">"];

const EMPTY = {
  sensor_id: SENSORS[0],
  operator: ">",
  threshold: "",
  unit: "",
  actuator_id: ACTUATORS[0],
  actuator_state: "ON",
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

    if (!form.threshold || isNaN(Number(form.threshold))) {
      setError("Threshold must be a valid number.");
      return;
    }

    try {
      await onSubmit({
        ...form,
        threshold: Number(form.threshold),
        unit: form.unit || null,
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
        <label>Sensor</label>
        <select name="sensor_id" value={form.sensor_id} onChange={handleChange}>
          {SENSORS.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
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
          name="threshold"
          value={form.threshold}
          onChange={handleChange}
          placeholder="e.g. 28"
          required
        />
      </div>

      <div className="rule-form__row">
        <label>Unit (optional)</label>
        <input
          type="text"
          name="unit"
          value={form.unit}
          onChange={handleChange}
          placeholder="e.g. °C"
        />
      </div>

      <div className="rule-form__row">
        <label>Actuator</label>
        <select name="actuator_id" value={form.actuator_id} onChange={handleChange}>
          {ACTUATORS.map((a) => <option key={a} value={a}>{a}</option>)}
        </select>
      </div>

      <div className="rule-form__row">
        <label>Set to</label>
        <select name="actuator_state" value={form.actuator_state} onChange={handleChange}>
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
        {loading ? "Saving…" : "Add Rule"}
      </button>
    </form>
  );
}
