// see note in actuatorApi.js about the extra path component – the
// service actually lives at `/api/rules`, so this keeps the front end and
// docs consistent and avoids odd proxy behavior.
const BASE = "/api/rules";

export async function fetchRules() {
  const res = await fetch(`${BASE}/`);
  if (!res.ok) throw new Error(`Rules API error: ${res.status}`);
  return res.json();
}

export async function createRule(data) {
  const res = await fetch(`${BASE}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to create rule");
  }
  return res.json();
}

export async function updateRule(ruleId, data) {
  const res = await fetch(`${BASE}/${ruleId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || `Failed to update rule ${ruleId}`);
  }
  return res.json();
}

export async function deleteRule(ruleId) {
  const res = await fetch(`${BASE}/${ruleId}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Failed to delete rule ${ruleId}`);
}
