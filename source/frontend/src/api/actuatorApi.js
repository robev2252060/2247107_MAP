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
      })`
    );
  }
  return res.json();
}
