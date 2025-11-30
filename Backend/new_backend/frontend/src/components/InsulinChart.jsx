import React from "react";

export default function InsulinChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="chart-empty">No data available</div>;
  }

  const values = data.map((d) => d.value);
  const minValue = Math.min(...values, 0);
  const maxValue = Math.max(...values, 4); // typical small doses in units

  const padding = 20;
  const width = 800;
  const height = 300;

  const toX = (index) =>
    padding +
    (index / Math.max(data.length - 1, 1)) * (width - padding * 2);

  const toY = (value) => {
    const normalized = (value - minValue) / (maxValue - minValue || 1);
    return height - padding - normalized * (height - padding * 2);
  };

  const pathD = data
    .map((point, i) => {
      const x = toX(i);
      const y = toY(point.value);
      return `${i === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

  return (
    <div className="chart-wrapper">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="none"
        className="chart-svg"
      >
        <rect x="0" y="0" width={width} height={height} className="chart-bg" />

        {/* Axes */}
        <line
          x1={padding}
          y1={height - padding}
          x2={width - padding}
          y2={height - padding}
          className="chart-axis"
        />
        <line
          x1={padding}
          y1={padding}
          x2={padding}
          y2={height - padding}
          className="chart-axis"
        />

        {/* Y labels & grid */}
        {[minValue, (minValue + maxValue) / 2, maxValue].map((v, idx) => (
          <g key={idx}>
            <line
              x1={padding - 5}
              y1={toY(v)}
              x2={width - padding}
              y2={toY(v)}
              className="chart-grid-line"
            />
            <text
              x={padding - 10}
              y={toY(v)}
              textAnchor="end"
              dominantBaseline="middle"
              className="chart-y-label"
            >
              {v.toFixed(1)}
            </text>
          </g>
        ))}

        {/* X labels */}
        {data.map((point, i) => (
          <text
            key={i}
            x={toX(i)}
            y={height - padding + 14}
            textAnchor="middle"
            className="chart-x-label"
          >
            {point.time}
          </text>
        ))}

        {/* Line */}
        <path d={pathD} className="chart-line insulin-line" fill="none" />

        {/* Points */}
        {data.map((point, i) => (
          <circle
            key={i}
            cx={toX(i)}
            cy={toY(point.value)}
            r="4"
            className="chart-point insulin-point"
          />
        ))}
      </svg>
    </div>
  );
}
