import { useState, useEffect } from "react";
import { getPollingRateMs, setPollingRateMs } from "../../api/pollingApi.js";

function fmtSeconds(ms) {
  return (ms / 1000).toFixed(1);
}

export default function PollingRateControl() {
  const [currentMs, setCurrentMs] = useState(null);
  const [inputSeconds, setInputSeconds] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const ms = await getPollingRateMs();
        if (cancelled) return;
        setCurrentMs(ms);
        setInputSeconds(fmtSeconds(ms));
      } catch (err) {
        if (cancelled) return;
        setError(err.message);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleSave = async () => {
    setError(null);
    setSuccessMsg(null);

    const parsed = Number(inputSeconds);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      setError("Polling rate must be a positive number (seconds).");
      return;
    }

    const ms = Math.round(parsed * 1000);

    setLoading(true);
    try {
      await setPollingRateMs(ms);
      setCurrentMs(ms);
      setSuccessMsg(`Polling rate updated to ${fmtSeconds(ms)}s.`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="rule-form" style={{ maxWidth: 360 }}>
      <h2>Polling Frequency</h2>
      <div className="rule-form__row">
        <label>Interval (seconds)</label>
        <input
          type="number"
          min={0.1}
          step={0.1}
          value={inputSeconds}
          onChange={(e) => setInputSeconds(e.target.value)}
          disabled={loading}
        />
      </div>
      <div className="rule-form__row" style={{ gap: 0.25, marginTop: 0.5 }}>
        <button className="btn btn--primary" onClick={handleSave} disabled={loading}>
          {loading ? "Saving…" : "Save"}
        </button>
        <span style={{ color: "var(--color-muted)", fontSize: "0.85rem" }}>
          Current: {currentMs != null ? fmtSeconds(currentMs) + "s" : "—"}
        </span>
      </div>
      {error && <div className="error-banner">{error}</div>}
      {successMsg && (
        <div className="toast toast--success" style={{ marginTop: "0.75rem" }}>
          <span className="toast__msg">{successMsg}</span>
        </div>
      )}
      <p style={{ fontSize: "0.75rem", color: "var(--color-muted)", marginTop: "0.5rem" }}>
        This setting controls how often the integration service polls legacy REST sensors.
      </p>
    </section>
  );
}
