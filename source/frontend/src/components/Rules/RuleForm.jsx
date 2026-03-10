import { useEffect, useMemo, useState } from "react";

const ACTUATORS = [
  "cooling_fan", "entrance_humidifier",
  "hall_ventilation", "habitat_heater",
];

const OPERATORS = ["<", "<=", "=", ">=", ">"];

const EMPTY = {
  sensor_source: "",
  sensor_metric: "",
  operator: ">",
  threshold_value: "",
  target_actuator: ACTUATORS[0],
  target_state: "ON",
  description: "",
};

export default function RuleForm({ onSubmit, loading, sourceMetrics }) {
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState(null);

  const sensorSources = useMemo(
    () => Object.keys(sourceMetrics || {}).sort((a, b) => a.localeCompare(b)),
    [sourceMetrics]
  );

  const availableMetrics = useMemo(
    () => (sourceMetrics?.[form.sensor_source] || []).slice().sort((a, b) => a.localeCompare(b)),
    [sourceMetrics, form.sensor_source]
  );

  useEffect(() => {
    if (sensorSources.length === 0) {
      if (form.sensor_source || form.sensor_metric) {
        setForm((prev) => ({ ...prev, sensor_source: "", sensor_metric: "" }));
      }
      return;
    }

    if (!sensorSources.includes(form.sensor_source)) {
      const nextSource = sensorSources[0];
      const nextMetric = (sourceMetrics?.[nextSource] || [])[0] || "";
      setForm((prev) => ({ ...prev, sensor_source: nextSource, sensor_metric: nextMetric }));
      return;
    }

    const metricsForSource = sourceMetrics?.[form.sensor_source] || [];
    if (!metricsForSource.includes(form.sensor_metric)) {
      setForm((prev) => ({ ...prev, sensor_metric: metricsForSource[0] || "" }));
    }
  }, [sensorSources, sourceMetrics, form.sensor_source, form.sensor_metric]);

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (!form.sensor_source) {
      setError("Sensor source is required.");
      return;
    }

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
      setForm((prev) => ({
        ...EMPTY,
        sensor_source: prev.sensor_source,
        sensor_metric: prev.sensor_metric,
      }));
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
        <select name="sensor_source" value={form.sensor_source} onChange={handleChange} disabled={sensorSources.length === 0}>
          {sensorSources.length === 0 ? (
            <option value="">Waiting for live measurements...</option>
          ) : (
            sensorSources.map((s) => <option key={s} value={s}>{s}</option>)
          )}
        </select>
      </div>

      <div className="rule-form__row">
        <label>Metric</label>
        <select name="sensor_metric" value={form.sensor_metric} onChange={handleChange} disabled={availableMetrics.length === 0}>
          {availableMetrics.length === 0 ? (
            <option value="">No metrics available</option>
          ) : (
            availableMetrics.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))
          )}
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

      <button className="btn btn--primary" type="submit" disabled={loading || sensorSources.length === 0 || availableMetrics.length === 0}>
        {loading ? "Saving..." : "Add Rule"}
      </button>
    </form>
  );
}
