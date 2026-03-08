// API base routes through Nginx gateway
const BASE = "/api/state";

/**
 * Fetch the latest state of all sensors.
 * @returns {Promise<Record<string, object>>}
 */
export async function fetchAllSensors() {
  const res = await fetch(`${BASE}/sensors`);
  if (!res.ok) throw new Error(`State API error: ${res.status}`);
  return res.json();
}

/**
 * Fetch the latest state of a single sensor.
 * @param {string} sensorId
 * @returns {Promise<object>}
 */
export async function fetchSensor(sensorId) {
  const res = await fetch(`${BASE}/sensors/${sensorId}`);
  if (!res.ok) throw new Error(`Sensor '${sensorId}' not found`);
  return res.json();
}

/**
 * Open an SSE connection to receive real-time sensor updates.
 * @param {(event: object) => void} onSnapshot   Called once with full snapshot
 * @param {(event: object) => void} onUpdate      Called on each sensor update
 * @returns {EventSource} — call .close() to disconnect
 */
export function openSensorStream(onSnapshot, onUpdate) {
  const es = new EventSource(`${BASE}/sensors/stream/sse`);

  es.addEventListener("snapshot", (e) => {
    onSnapshot(JSON.parse(e.data));
  });

  es.addEventListener("sensor_update", (e) => {
    onUpdate(JSON.parse(e.data));
  });

  es.onerror = (err) => {
    console.error("SSE error:", err);
  };

  return es;
}
