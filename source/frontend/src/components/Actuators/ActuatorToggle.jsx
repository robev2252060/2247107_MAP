const ACTUATOR_ICONS = {
  cooling_fan:          "🌀",
  entrance_humidifier:  "💦",
  hall_ventilation:     "🌬️",
  habitat_heater:       "🔥",
};

export default function ActuatorToggle({ actuator, onToggle }) {
  const isOn  = actuator.state === "ON";
  const id    = actuator.id || actuator.name;
  const icon  = ACTUATOR_ICONS[id] ?? "⚡";
  const label = id.replace(/_/g, " ");

  return (
    <div className={`actuator-toggle ${isOn ? "actuator-toggle--on" : "actuator-toggle--off"}`}>
      <span className="actuator-toggle__icon">{icon}</span>
      <span className="actuator-toggle__label">{label}</span>
      <button
        className={`btn ${isOn ? "btn--danger" : "btn--primary"}`}
        onClick={() => onToggle(isOn ? "OFF" : "ON")}
      >
        {isOn ? "Turn OFF" : "Turn ON"}
      </button>
    </div>
  );
}
