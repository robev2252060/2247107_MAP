import { useMemo } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

function formatTime(date) {
  if (!(date instanceof Date)) date = new Date(date);
  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default function SensorLineChart({ sensorKey, data }) {
  const chartData = useMemo(() => {
    if (!Array.isArray(data)) return [];
    return data.map((point) => ({
      time: point.time instanceof Date ? point.time : new Date(point.time),
      value: point.value,
    }));
  }, [data]);

  if (!sensorKey) {
    return (
      <div style={{ padding: "1rem", color: "var(--color-muted)" }}>
        Select a sensor to view its live chart.
      </div>
    );
  }

  return (
    <div
      style={{
        width: "100%",
        height: 320,
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius)",
        padding: "1rem",
      }}
    >
      <div
        style={{
          fontSize: "0.95rem",
          marginBottom: "0.75rem",
          fontWeight: 600,
        }}
      >
        Live Chart: {sensorKey}
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid stroke="#2a3148" strokeDasharray="4 4" />
          <XAxis
            dataKey="time"
            tickFormatter={formatTime}
            stroke="var(--color-muted)"
            tick={{ fontSize: 11 }}
            minTickGap={20}
          />
          <YAxis stroke="var(--color-muted)" tick={{ fontSize: 11 }} />
          <Tooltip
            formatter={(value) => [value, "value"]}
            labelFormatter={(label) => `Time: ${formatTime(label)}`}
            contentStyle={{
              backgroundColor: "var(--color-surface)",
              border: "1px solid var(--color-border)",
              color: "var(--color-text)",
            }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="var(--color-primary)"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
