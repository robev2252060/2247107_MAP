// the gateway exposes actuator endpoints under `/api/actuators`
// older docs (and early versions) referred to `/api/actuators/actuators` but
// the extra segment is unnecessary and could confuse the proxy. keep the
// base simple so requests map cleanly through nginx.
const BASE = "/api/actuators";

export async function fetchActuators() {
  const res = await fetch(`${BASE}`);
  if (!res.ok) {
    // try to include response body if available for easier debugging
    let text;
    try {
      text = await res.text();
    } catch {
      text = "";
    }
    throw new Error(
      `Actuators API error: ${res.status}${text ? ` – ${text}` : ""}`
    );
  }
  return res.json();
}

/**
 * @param {string} actuatorId
 * @param {"ON"|"OFF"} state
 */
export async function setActuatorState(actuatorId, state) {
  const res = await fetch(`${BASE}/${actuatorId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state }),
  });
  if (!res.ok) {
    let errText;
    try {
      errText = await res.text();
    } catch {
      errText = "";
    }
    throw new Error(
      `Failed to set actuator ${actuatorId} (${res.status}${
        errText ? ` – ${errText}` : ""}
      )`
    );
  }
  return res.json();
}

/**
 * Streams actuator state changes as MeasurementEvent SSE.
 * @param {(event: object) => void} onMeasurement
 * @returns {EventSource}
 */
export function openActuatorStream(onMeasurement) {
  const es = new EventSource(`${BASE}/stream`);

  es.addEventListener("measurement", (e) => {
    onMeasurement(JSON.parse(e.data));
  });

  es.onerror = (err) => {
    console.error("Actuator SSE error:", err);
  };

  return es;
}
