import React from "react";

/**
 * Simple vertical CGM-style meter.
 * - Shows current glucose value.
 * - Fills the bar based on a min/max range.
 * - Highlights whether the value is low / in range / high.
 */
export default function GlucoseMeter({
  value,
  min = 40,
  max = 250,
  targetMin = 80,
  targetMax = 160,
}) {
  const clamped = Math.min(Math.max(value ?? 0, min), max);
  const percent = ((clamped - min) / (max - min || 1)) * 100;

  let status = "in-range";
  if (value < targetMin) status = "low";
  else if (value > targetMax) status = "high";

  const statusLabel =
    status === "low" ? "Below range" : status === "high" ? "Above range" : "In target range";

  return (
    <div className={`meter-root meter-${status}`}>
      <div className="meter-header">
        <div>
          <p className="meter-label">Live CGM Meter</p>
          <p className="meter-status-text">{statusLabel}</p>
        </div>
        <div className="meter-reading">
          <span className="meter-value">{value ?? "--"}</span>
          <span className="meter-unit">mg/dL</span>
        </div>
      </div>

      <div className="meter-body">
        <div className="meter-rail">
          {/* Target band in the middle of the rail */}
          <div className="meter-target-band" />
          {/* Fill from bottom based on current percentage */}
          <div className="meter-fill" style={{ height: `${percent}%` }} />
        </div>
        <div className="meter-scale">
          <span>{max}</span>
          <span>{targetMax}</span>
          <span>{targetMin}</span>
          <span>{min}</span>
        </div>
      </div>
    </div>
  );
}
