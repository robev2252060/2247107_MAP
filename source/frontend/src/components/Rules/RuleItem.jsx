import { useState } from "react";

const TELEMETRY_PREFIX = "mars/telemetry/";

function toFinalSourceIdentifier(source) {
  if (!source) return source;
  return source.startsWith(TELEMETRY_PREFIX)
    ? source.slice(TELEMETRY_PREFIX.length)
    : source;
}

export default function RuleItem({ rule, onDelete, onToggle, onEdit }) {
  const [isEditMode, setIsEditMode] = useState(false);
  const [editThreshold, setEditThreshold] = useState(String(rule.threshold_value));
  const [saving, setSaving] = useState(false);

  const source = toFinalSourceIdentifier(rule.sensor_source);
  const condition = `IF ${source}.${rule.sensor_metric} ${rule.operator} ${rule.threshold_value}`;
  const action    = `THEN set ${rule.target_actuator} to ${rule.target_state}`;

  async function handleSave() {
    if (!editThreshold || isNaN(Number(editThreshold))) {
      alert("Please enter a valid threshold value");
      return;
    }

    setSaving(true);
    try {
      await onEdit(rule.id, Number(editThreshold));
      setIsEditMode(false);
    } finally {
      setSaving(false);
    }
  }

  function handleCancel() {
    setEditThreshold(String(rule.threshold_value));
    setIsEditMode(false);
  }

  if (isEditMode) {
    return (
      <li className="rule-item rule-item--edit">
        <div className="rule-item__edit-form">
          <div className="rule-item__edit-field">
            <label>Threshold:</label>
            <input
              type="number"
              step="any"
              value={editThreshold}
              onChange={(e) => setEditThreshold(e.target.value)}
              disabled={saving}
              autoFocus
            />
          </div>
          <div className="rule-item__edit-actions">
            <button
              className="btn btn--sm btn--primary"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? "Saving..." : "Save"}
            </button>
            <button
              className="btn btn--sm btn--ghost"
              onClick={handleCancel}
              disabled={saving}
            >
              Cancel
            </button>
          </div>
        </div>
      </li>
    );
  }

  return (
    <li className={`rule-item ${rule.enabled ? "" : "rule-item--disabled"}`}>
      <div className="rule-item__body">
        <code className="rule-item__condition">{condition}</code>
        <code className="rule-item__action">{action}</code>
        {rule.description && (
          <span className="rule-item__desc">{rule.description}</span>
        )}
      </div>
      <div className="rule-item__actions">
        <button
          className="btn btn--sm btn--ghost"
          onClick={() => setIsEditMode(true)}
          title="Edit rule threshold"
        >
          Edit
        </button>
        <button
          className="btn btn--sm btn--ghost"
          onClick={onToggle}
          title={rule.enabled ? "Disable rule" : "Enable rule"}
        >
          {rule.enabled ? "Disable" : "Enable"}
        </button>
        <button
          className="btn btn--sm btn--danger"
          onClick={onDelete}
          title="Delete rule"
        >
          Delete
        </button>
      </div>
    </li>
  );
}
