const BASE = "/api/integration";

/**
 * Open an SSE connection to receive normalized measurement events.
 * @param {(event: object) => void} onMeasurement
 * @returns {EventSource}
 */
export function openMeasurementStream(onMeasurement) {
  const es = new EventSource(`${BASE}/sensors/stream`);

  es.addEventListener("measurement", (e) => {
    onMeasurement(JSON.parse(e.data));
  });

  es.onerror = (err) => {
    console.error("Integration SSE error:", err);
  };

  return es;
}

