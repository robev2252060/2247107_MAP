import { useState, useEffect, useCallback } from "react";
import { fetchActuators, setActuatorState } from "../api/actuatorApi.js";
import ActuatorPanel from "../components/Actuators/ActuatorPanel.jsx";

export default function ActuatorsPage() {
  const [actuators, setActuators] = useState([]);
  const [error, setError]         = useState(null);

  const loadActuators = useCallback(async () => {
    try {
      setError(null);
      const data = await fetchActuators();
      setActuators(data);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  // Initial load + poll every 5 s to reflect rule-triggered state changes
  useEffect(() => {
    loadActuators();
    const id = setInterval(loadActuators, 5000);
    return () => clearInterval(id);
  }, [loadActuators]);

  async function handleToggle(actuatorId, newState) {
    try {
      await setActuatorState(actuatorId, newState);
      setActuators((prev) =>
        prev.map((a) =>
          (a.actuator_name) === actuatorId ? { ...a, state: newState } : a
        )
      );
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="page">
      <h1>Actuator Control</h1>
      {error && <div className="error-banner">{error}</div>}
      <ActuatorPanel actuators={actuators} onToggle={handleToggle} />
    </section>
  );
}
