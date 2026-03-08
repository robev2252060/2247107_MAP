import ActuatorToggle from "./ActuatorToggle.jsx";

export default function ActuatorPanel({ actuators, onToggle }) {
  if (!actuators || actuators.length === 0) {
    return <p className="empty-state">No actuators available.</p>;
  }

  return (
    <div className="actuator-panel">
      {actuators.map((a) => (
        <ActuatorToggle
          key={a.id || a.name}
          actuator={a}
          onToggle={(newState) => onToggle(a.id || a.name, newState)}
        />
      ))}
    </div>
  );
}
