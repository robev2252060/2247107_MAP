import RuleItem from "./RuleItem.jsx";

export default function RuleList({ rules, onDelete, onToggle, onEdit }) {
  if (rules.length === 0) {
    return <p className="empty-state">No automation rules defined yet.</p>;
  }

  return (
    <ul className="rule-list">
      {rules.map((rule) => (
        <RuleItem
          key={rule.id}
          rule={rule}
          onDelete={() => onDelete(rule.id)}
          onToggle={() => onToggle(rule.id, !rule.enabled)}
          onEdit={(ruleId, newThreshold) => onEdit(ruleId, newThreshold)}
        />
      ))}
    </ul>
  );
}
