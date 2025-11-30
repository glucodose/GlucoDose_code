import React, { useState, useEffect, useRef } from "react";
import GlucoseChart from "./components/GlucoseChart";
import InsulinChart from "./components/InsulinChart";
import GlucoseGauge from "./components/GlucoseGauge";
import "./styles.css";

const SOCKET_URL = "ws://127.0.0.1:8000/ws/glucose";
const SPIKE_URL = "http://127.0.0.1:8000/spike";
const START_URL = "http://127.0.0.1:8000/start";
const STOP_URL = "http://127.0.0.1:8000/stop";
const COOLER_URL = "http://127.0.0.1:8000/cooler";

export default function App() {
  const [socketData, setSocketData] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState("Disconnected");
  const ws = useRef(null);

  useEffect(() => {
    const connect = () => {
      setConnectionStatus("Connecting...");
      ws.current = new WebSocket(SOCKET_URL);
      ws.current.onopen = () => setConnectionStatus("Connected");
      ws.current.onmessage = (event) => { try { setSocketData(JSON.parse(event.data)); } catch (e) { } };
      ws.current.onclose = () => { setConnectionStatus("Disconnected"); setTimeout(connect, 3000); };
    };
    connect();
    return () => { if (ws.current) ws.current.close(); };
  }, []);

  const handleInitiate = async () => { try { await fetch(SPIKE_URL, { method: "POST" }); } catch (e) { } };

  const handleToggleSystem = async () => {
    const isRunning = socketData?.isRunning;
    const url = isRunning ? STOP_URL : START_URL;
    try { await fetch(url, { method: "POST" }); } catch (e) { }
  };

  const handleCooler = async () => {
    try { await fetch(COOLER_URL, { method: "POST" }); } catch (e) { }
  };

  // Data Parsing
  const glucoseHistory = socketData?.glucoseHistory || [];
  const basalHistory = socketData?.basalHistory || [];
  const formattedGlucoseData = glucoseHistory.map((item) => ({
    time: new Date(item.ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
    value: item.bg,
  }));
  const formattedInsulinData = basalHistory.map((item) => ({
    time: new Date(item.ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
    value: item.rate,
  }));

  const currentBG = socketData?.currentBG || 0;
  const currentIOB = socketData?.currentIOB || 0;
  const prediction = socketData?.latestRecommendation?.eventualBG || "--";
  const algoReason = socketData?.latestRecommendation?.reason || "Waiting...";
  const suggestedBasal = socketData?.latestRecommendation?.rate || 0.0;
  const motorState = socketData?.motorState || "OFF";
  const pumpStats = socketData?.pumpStats || { plunger_mm: 0, rotations: 0, pulses: 0 };
  const isRunning = socketData?.isRunning || false;

  const insulinTemp = socketData?.insulinTemp || "--";
  const coolerState = socketData?.coolerState || "OFF";

  const rotationPct = Math.min((pumpStats.rotations / 1.5) * 100, 100);

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">Glucodose</div>

        {/* CENTER DEMO TEXT */}
        <div className="demo-badge">DEMO VERSION</div>

        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button className={`nav-btn ${isRunning ? "btn-stop" : "btn-start"}`} onClick={handleToggleSystem}>
            {isRunning ? "⏸ PAUSE" : "▶ START"}
          </button>
          <span className="nav-btn" style={{ color: connectionStatus === "Connected" ? "#4ade80" : "#ef4444" }}>
            {connectionStatus}
          </span>
        </div>
      </header>

      <main className="app-main">
        <section className="card stats-card">
          <h2>Monitor Panel</h2>
          <div className="vertical-panels-grid">

            {/* PANEL 1 */}
            <div className="vertical-panel">
              <h3 className="panel-title">Glucose Trend</h3>
              {/* Max gauge increased to 400 for High BG scenario */}
              <GlucoseGauge value={currentBG} max={400} />
              <div style={{ marginTop: "0.75rem", flex: 1 }}>
                <GlucoseChart data={formattedGlucoseData} />
              </div>
              <div className="chart-legend-bottom">
                <div className="legend-item"><span className="legend-dot legend-glucose"></span><span>Live BG</span></div>
              </div>
            </div>

            {/* PANEL 2 */}
            <div className="vertical-panel">
              <h3 className="panel-title panel-title-center">Gluco-1 (Algorithm)</h3>
              <div className="panel-chart-wrapper"><InsulinChart data={formattedInsulinData} /></div>
              <div className="panel-notes" style={{ overflowY: 'auto', fontFamily: 'monospace', fontSize: '0.75rem', lineHeight: '1.2', marginTop: '10px' }}>
                <strong style={{ color: '#a855f7' }}>Decision Logic:</strong><br />{algoReason}
              </div>
              <div className="delivery-stats" style={{ marginTop: '1rem' }}>
                <div className="delivery-item">
                  <span className="item-label">Active IOB</span>
                  <span className="item-value" style={{ color: '#3b82f6' }}>{currentIOB} U</span>
                </div>
                <div className="delivery-item">
                  <span className="item-label">Predicted BG</span>
                  <span className="item-value" style={{ color: prediction > 120 ? '#f97316' : '#22c55e' }}>{prediction} mg/dL</span>
                </div>
                <div className="delivery-item">
                  <span className="item-label">Sug. Basal Rate</span>
                  <span className="item-value">{suggestedBasal.toFixed(2)} U/hr</span>
                </div>
              </div>
            </div>

            {/* PANEL 3 */}
            <div className="vertical-panel">
              <h3 className="panel-title panel-title-center">Device Mechanics</h3>

              <div className="loop-status" style={{ marginTop: '0.5rem', marginBottom: '0.5rem' }}>
                <span className="loop-dot" style={{ background: motorState === "ON" ? "#3b82f6" : "#22c55e", boxShadow: motorState === "ON" ? "0 0 10px #3b82f6" : "none" }}></span>
                Motor: {motorState === "ON" ? "ROTATING" : "IDLE"}
              </div>

              <div className="mechanic-box">
                <div className="mechanic-label">Motor Rotation</div>
                <div className="mechanic-big-value">{pumpStats.rotations.toFixed(4)} <span className="mechanic-unit">rot</span></div>
                <div className="rotation-bar-bg">
                  <div className="rotation-bar-fill" style={{ width: `${rotationPct}%` }}></div>
                </div>
              </div>

              {/* RESTORED: PULSES & PLUNGER ROW */}
              <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                <div className="mechanic-box small">
                  <div className="mechanic-label">Enc. Pulses</div>
                  <div className="mechanic-mid-value">{pumpStats.pulses}</div>
                </div>
                <div className="mechanic-box small">
                  <div className="mechanic-label">Plunger</div>
                  <div className="mechanic-mid-value">{pumpStats.plunger_mm.toFixed(4)}<span className="mechanic-unit-sm">mm</span></div>
                </div>
              </div>

              {/* COOLER & TEMP SECTION */}
              <div className="mechanic-box" style={{ marginTop: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ textAlign: 'left' }}>
                  <div className="mechanic-label">Insulin Temp</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 'bold', color: coolerState === "ON" ? '#60a5fa' : '#e2e8f0' }}>
                    {insulinTemp}°C
                  </div>
                </div>
                <button
                  className={`cooler-btn ${coolerState === "ON" ? "cooler-active" : ""}`}
                  onClick={handleCooler}
                >
                  ❄️ COOL
                </button>
              </div>

              <button
                className={`view-history-btn ${motorState === "ON" ? "injecting-active" : ""}`}
                onClick={handleInitiate}
                disabled={!isRunning}
                style={{ marginTop: 'auto', border: 'none', fontWeight: 'bold', fontSize: '1rem', padding: '12px', transition: 'all 0.3s ease', opacity: isRunning ? 1 : 0.5 }}
              >
                INITIATE SEQUENCE
              </button>
            </div>

          </div>
        </section>
      </main>

      <footer className="app-footer"><span>Glucodose System</span></footer>
    </div>
  );
}