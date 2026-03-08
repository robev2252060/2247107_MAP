export default function RuleItem({ rule, onDelete, onToggle }) {
  const condition = `IF ${rule.sensor_id} ${rule.operator} ${rule.threshold}${rule.unit ? ` ${rule.unit}` : ""}`;
  const action    = `THEN set ${rule.actuator_id} to ${rule.actuator_state}`;

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
