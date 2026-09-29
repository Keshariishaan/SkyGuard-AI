const Header = ({ tab, setTab }) => (
  <header><div className="wrap hd">
    <div className="logo">🛡</div>
    <div><h1>SkyGuard AI</h1><span className="badge">Sensor anomaly system</span>
      <div className="sub">Hardware Sensor Ingestion, Isolation Forest Detection &amp; Fault Classification</div></div>
    <nav className="nav">{[["tel", "〜 Interactive Telemetry"], ["app", "›_ app.py (Streamlit)"], ["docs", "⚙ Pipeline Docs"]].map(([k, l]) =>
      <button key={k} className={tab === k ? "on" : ""} onClick={() => setTab(k)}>{l}</button>)}</nav>
  </div></header>
);
