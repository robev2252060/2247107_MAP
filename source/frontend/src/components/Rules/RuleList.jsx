import RuleItem from "./RuleItem.jsx";

export default function RuleList({ rules, onDelete, onToggle }) {
  if (rules.length === 0) {
    return <p className="empty-state">No automation rules defined yet.</p>;
  }

  return (
    <ul className="rule-list">
      {rules.map((rule) => (
        <RuleItem
          key={rule._id}
          rule={rule}
          onDelete={() => onDelete(rule._id)}
          onToggle={() => onToggle(rule._id, !rule.enabled)}
        />
      ))}
    </ul>
  );
}
