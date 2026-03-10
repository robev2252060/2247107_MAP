import { useState, useEffect, useCallback } from "react";
import { fetchActuators, openActuatorStream, setActuatorState } from "../api/actuatorApi.js";
import ActuatorPanel from "../components/Actuators/ActuatorPanel.jsx";

function applyMeasurement(prev, event) {
  const actuatorId = event?.source;
  const stateReading = (event?.readings || []).find((r) => r.metric === "state");
  const newState = stateReading?.value;

  if (!actuatorId || (newState !== "ON" && newState !== "OFF")) {
    return prev;
  }

  const idx = prev.findIndex((a) => a.actuator_name === actuatorId);
  if (idx === -1) {
    return [...prev, { actuator_name: actuatorId, state: newState }];
  }

  return prev.map((a) =>
    a.actuator_name === actuatorId ? { ...a, state: newState } : a
  );
}

export default function ActuatorsPage() {
  const [actuators, setActuators] = useState([]);
  const [error, setError] = useState(null);

  const loadActuators = useCallback(async () => {
    try {
      setError(null);
      const data = await fetchActuators();
      setActuators(data);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    loadActuators();

    const es = openActuatorStream((event) => {
      setActuators((prev) => applyMeasurement(prev, event));
    });

    es.onerror = () => {
      setError("Lost actuator stream connection - retrying...");
    };

    return () => es.close();
  }, [loadActuators]);

  async function handleToggle(actuatorId, newState) {
    try {
      await setActuatorState(actuatorId, newState);
      setActuators((prev) =>
        prev.map((a) =>
          a.actuator_name === actuatorId ? { ...a, state: newState } : a
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
