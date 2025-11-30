import React from "react";

export default function GlucoseGauge({
  value,
  min = 40,
  max = 250,
  targetMin = 80,
  targetMax = 160,
}) {
  const safeValue = value ?? 0;
  const clamped = Math.min(Math.max(safeValue, min), max);
  const percent = ((clamped - min) / (max - min || 1)) * 100;

  let status = "in-range";
  if (safeValue < targetMin) status = "low";
  else if (safeValue > targetMax) status = "high";

  const statusLabel =
    status === "low"
      ? "Below range"
      : status === "high"
      ? "Above range"
      : "In target range";

  const color =
    status === "low"
      ? "#f97316"
      : status === "high"
      ? "#ef4444"
      : "#22c55e";

  return (
    <div className={`gauge-root gauge-${status}`}>
      <div className="gauge-header">
        <span className="gauge-label">Current Glucose</span>
        <span className="gauge-time">Now</span>
      </div>

      <div className="gauge-body">
        <svg viewBox="0 0 200 110" className="gauge-svg">
          {/* background arc */}
          <path
            className="gauge-arc-bg"
            d="M 20 100 A 80 80 0 0 1 180 100"
          />

          {/* value arc */}
          <path
            className="gauge-arc-fill"
            d="M 20 100 A 80 80 0 0 1 180 100"
            pathLength="100"
            style={{
              strokeDasharray: "100",
              strokeDashoffset: `${100 - percent}`,
              stroke: color,
            }}
          />
        </svg>

        <div className="gauge-center">
          <div className="gauge-value">
            {value != null ? value : "--"}
          </div>
          <div className="gauge-unit">mg/dL</div>
          <div className="gauge-status-chip">{statusLabel}</div>
        </div>
      </div>
    </div>
  );
}
