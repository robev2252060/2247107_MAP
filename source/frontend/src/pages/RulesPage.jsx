import { useState, useEffect, useCallback } from "react";
import { fetchRules, createRule, updateRule, deleteRule } from "../api/ruleApi.js";
import RuleList from "../components/Rules/RuleList.jsx";
import RuleForm from "../components/Rules/RuleForm.jsx";

export default function RulesPage() {
  const [rules, setRules]     = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const loadRules = useCallback(async () => {
    try {
      setError(null);
      const data = await fetchRules();
      setRules(data);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => { loadRules(); }, [loadRules]);

  async function handleCreate(data) {
    setLoading(true);
    try {
      await createRule(data);
      await loadRules();
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(ruleId) {
    await deleteRule(ruleId);
    setRules((prev) => prev.filter((r) => r._id !== ruleId));
  }

  async function handleToggle(ruleId, enabled) {
    await updateRule(ruleId, { enabled });
    setRules((prev) =>
      prev.map((r) => (r._id === ruleId ? { ...r, enabled } : r))
    );
  }

  return (
    <section className="page">
      <h1>Automation Rules</h1>
      {error && <div className="error-banner">{error}</div>}
      <div className="rules-layout">
        <RuleForm onSubmit={handleCreate} loading={loading} />
        <RuleList rules={rules} onDelete={handleDelete} onToggle={handleToggle} />
      </div>
    </section>
  );
}
