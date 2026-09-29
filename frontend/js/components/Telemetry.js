const Telemetry = ({ rows, p }) => {
  const [view, setView] = useState("temperature"), [marks, setMarks] = useState(true);
  const notes = {
    temperature: `Look for extreme spike around Hour ${p.spikeH} (${p.spikeT}°C)`,
    humidity: `Look for ${p.frozenD}-hour flatline around Hour ${p.frozenH}`,
    pressure: `Look for ${p.driftD}-hour upward drift around Hour ${p.driftH}`,
    combined: "",
  };
  return (
    <section className="panel">
      <div className="ch">
        <div>
          <h3>Hardware Sensor Telemetry Time Series</h3> <span className="badge">{rows.length} Hourly Readings</span>
          <div className="sub">Red markers highlight data points flagged as anomalous by the Isolation Forest model</div>
        </div>
        <div className="tabs">
          {[["temperature", "🌡 Temperature"], ["humidity", "💧 Humidity"], ["pressure", "◎ Pressure"], ["combined", "Combined"]].map(([k, l]) => (
            <button key={k} className={view === k ? "on" : ""} onClick={() => setView(k)}>{l}</button>
          ))}
        </div>
      </div>
      <div className="leg">
        <span>
          <span className="dot" /><b style={{ color: "#be123c", fontWeight: 600 }}>Red Alert Marker:</b>{" "}
          <span style={{ color: "var(--ink)" }}>Detected Sensor Anomaly</span> &nbsp;&nbsp; {notes[view] && "Note: " + notes[view]}
        </span>
        <label style={{ color: "var(--ink)" }}>
          <input type="checkbox" checked={marks} onChange={(e) => setMarks(e.target.checked)} /> Highlight anomaly markers
        </label>
      </div>
      <Chart rows={rows} view={view} marks={marks} />
    </section>
  );
};
