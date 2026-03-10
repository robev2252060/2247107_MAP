const TELEMETRY_PREFIX = "mars/telemetry/";

function toFinalSourceIdentifier(source) {
  if (!source) return source;
  return source.startsWith(TELEMETRY_PREFIX)
    ? source.slice(TELEMETRY_PREFIX.length)
    : source;
}

export default function RuleItem({ rule, onDelete, onToggle }) {
  const source = toFinalSourceIdentifier(rule.sensor_source);
  const condition = `IF ${source}.${rule.sensor_metric} ${rule.operator} ${rule.threshold_value}`;
  const action    = `THEN set ${rule.target_actuator} to ${rule.target_state}`;

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
