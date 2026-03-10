import { useState, useEffect, useCallback } from "react";
import { fetchRules, createRule, updateRule, deleteRule } from "../api/ruleApi.js";
import { openMeasurementStream } from "../api/integrationApi.js";
import RuleList from "../components/Rules/RuleList.jsx";
import RuleForm from "../components/Rules/RuleForm.jsx";

const TELEMETRY_PREFIX = "mars/telemetry/";

function toFinalSourceIdentifier(source) {
  if (!source) return source;
  return source.startsWith(TELEMETRY_PREFIX)
    ? source.slice(TELEMETRY_PREFIX.length)
    : source;
}

function normalizeRule(rule) {
  return {
    ...rule,
    sensor_source: toFinalSourceIdentifier(rule.sensor_source),
  };
}

export default function RulesPage() {
  const [rules, setRules] = useState([]);
  const [sourceMetrics, setSourceMetrics] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const upsertSourceMetrics = useCallback((source, metrics) => {
    if (!source || metrics.length === 0) return;

    setSourceMetrics((prev) => {
      const existing = prev[source] || [];
      const merged = Array.from(new Set([...existing, ...metrics]));
      if (merged.length === existing.length) return prev;
      return { ...prev, [source]: merged };
    });
  }, []);

  const loadRules = useCallback(async () => {
    try {
      setError(null);
      const data = await fetchRules();
      const normalized = data.map(normalizeRule);
      setRules(normalized);

      normalized.forEach((rule) => {
        upsertSourceMetrics(rule.sensor_source, [rule.sensor_metric]);
      });
    } catch (err) {
      setError(err.message);
    }
  }, [upsertSourceMetrics]);

  useEffect(() => {
    loadRules();
  }, [loadRules]);

  useEffect(() => {
    const es = openMeasurementStream((event) => {
      const source = toFinalSourceIdentifier(event?.source);
      const metrics = (event?.readings || [])
        .map((r) => r?.metric)
        .filter(Boolean);
      upsertSourceMetrics(source, metrics);
    });

    return () => es.close();
  }, [upsertSourceMetrics]);

  async function handleCreate(data) {
    setLoading(true);
    try {
      const payload = {
        ...data,
        sensor_source: toFinalSourceIdentifier(data.sensor_source),
      };
      await createRule(payload);
      await loadRules();
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(ruleId) {
    await deleteRule(ruleId);
    setRules((prev) => prev.filter((r) => r.id !== ruleId));
  }

  async function handleToggle(ruleId, enabled) {
    const current = rules.find((r) => r.id === ruleId);
    if (!current) return;

    const payload = {
      sensor_source: toFinalSourceIdentifier(current.sensor_source),
      sensor_metric: current.sensor_metric,
      operator: current.operator,
      threshold_value: current.threshold_value,
      target_actuator: current.target_actuator,
      target_state: current.target_state,
      enabled,
      description: current.description ?? null,
    };

    const updated = await updateRule(ruleId, payload);
    setRules((prev) => prev.map((r) => (r.id === ruleId ? normalizeRule(updated) : r)));
  }

  return (
    <section className="page">
      <h1>Automation Rules</h1>
      {error && <div className="error-banner">{error}</div>}
      <div className="rules-layout">
        <RuleForm onSubmit={handleCreate} loading={loading} sourceMetrics={sourceMetrics} />
        <RuleList rules={rules} onDelete={handleDelete} onToggle={handleToggle} />
      </div>
    </section>
  );
}
