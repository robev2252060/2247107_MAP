const BASE = "/api/integration";

/**
 * Get the current global polling rate (milliseconds) used by the integration service.
 * @returns {Promise<number>} polling rate in milliseconds
 */
export async function getPollingRateMs() {
  const res = await fetch(`${BASE}/polling/rate`);
  if (!res.ok) throw new Error(`Polling API error: ${res.status}`);
  return res.json();
}

/**
 * Update the global polling rate (milliseconds) used by the integration service.
 * @param {number} rateMs
 */
export async function setPollingRateMs(rateMs) {
  const res = await fetch(`${BASE}/polling/rate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rate: rateMs }),
  });
  if (!res.ok) {
    throw new Error(`Failed to set polling rate: ${res.status}`);
  }
}
