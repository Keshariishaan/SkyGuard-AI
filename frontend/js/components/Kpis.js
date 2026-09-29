const Kpi = ({ cls, label, icon, value, note, extra }) => (
  <div className={"kpi " + cls}><div className="l"><span>{label}</span><span>{icon}</span></div>
    <div className="v">{value}{extra}</div><div className="n">{note}</div></div>
);

// kpis comes straight from the backend response (POST /api/telemetry) -
// counts are computed server-side by backend/services/telemetry_service.py.
const Kpis = ({ kpis }) => (
  <div className="kpis">
    <Kpi cls="" label="Total telemetry" icon="≣" value={kpis.total} note="Hourly weather sensor rows" />
    <Kpi cls="k1" label="Anomalies flagged" icon="⚠" value={kpis.anomalies}
      extra={<span className="rate">{((kpis.anomalies / kpis.total) * 100).toFixed(0)}% rate</span>}
      note="Flagged by Isolation Forest" />
    <Kpi cls="k2" label="Spike faults" icon="ϟ" value={kpis.spike} note="Thermal spikes (extreme temp)" />
    <Kpi cls="k3" label="Frozen faults" icon="❄" value={kpis.frozen} note="Static zero-variance humidity" />
    <Kpi cls="k4" label="Drift faults" icon="↗" value={kpis.drift} note="Barometric upward creep" />
  </div>
);
