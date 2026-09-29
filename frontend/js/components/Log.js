const Log = ({ rows, p }) => {
  const [f, setF] = useState("All"), [q, setQ] = useState(""), [pg, setPg] = useState(0);
  const match = (x, k) => k === "All" || (k === "Anomalies" ? x.anomaly : x.diagnosis === k);
  const chips = [["All", "All"], ["Anomalies", "All Anomalies"], ["Spike", "Spikes"], ["Frozen", "Frozen"], ["Drift", "Drift"]];
  const ql = q.trim().toLowerCase();
  const v = rows.filter((x) => match(x, f) && (!ql || ("hour " + x.h).includes(ql) || fmt(x.ts).includes(ql)));
  const pages = Math.max(1, Math.ceil(v.length / PAGE_SIZE)), cur = Math.min(pg, pages - 1);
  const sl = v.slice(cur * PAGE_SIZE, cur * PAGE_SIZE + PAGE_SIZE);

  const exp = () => { Api.downloadCsv(p).catch((e) => console.error(e)); };

  return (
    <section className="panel" style={{ padding: 0, overflow: "hidden" }}>
      <div className="prow" style={{ padding: "22px 18px 16px" }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 21, display: "inline" }}>Telemetry &amp; Anomaly Diagnostic Log</h3>{" "}
          <span className="badge">{v.length} records matching</span>
          <div className="sub">Model predictions compared against injected ground truth faults</div>
        </div>
        <div className="ml">
          <input className="search" placeholder="Search hour or date..." value={q} onChange={(e) => { setQ(e.target.value); setPg(0); }} />
          <button className="pill" onClick={exp}>⤓ Export CSV</button>
        </div>
      </div>
      <div className="fl">
        <span style={{ color: "var(--mut)" }}>▽ Filter:</span>
        {chips.map(([k, l]) => (
          <button key={k} className={f === k ? "on" : ""} onClick={() => { setF(k); setPg(0); }}>
            {l} ({rows.filter((x) => match(x, k)).length})
          </button>
        ))}
      </div>
      <div className="tw" style={{ margin: 0, border: 0, borderRadius: 0, maxHeight: "none" }}>
        <table className="lg">
          <thead>
            <tr>
              {["Hour / Timestamp", "Temperature", "Humidity", "Pressure", "Anomaly Status", "RF Classification", "Ground Truth", "Anomaly Score"].map((h, i) => (
                <th key={h} style={i === 7 ? { textAlign: "right" } : null}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sl.map((x) => (
              <tr key={x.h} className={x.anomaly ? "an" : ""}>
                <td><b>Hour {x.h}</b> <span className="mono mut">{fmt(x.ts)}</span></td>
                <td className="mono">{x.temperature.toFixed(2)} °C</td>
                <td className="mono">{x.humidity.toFixed(2)} %</td>
                <td className="mono">{x.pressure.toFixed(2)} hPa</td>
                <td>{x.anomaly ? <span style={{ color: "#be123c", fontWeight: 500 }}>● Anomaly (-1)</span> : <span className="mut">Normal (1)</span>}</td>
                <td><span className={"rf " + x.diagnosis}>{ICON[x.diagnosis]} {x.diagnosis}</span></td>
                <td><span className="gt">{x.truth}</span></td>
                <td className="mono" style={{ textAlign: "right", color: x.anomaly ? "#be123c" : "var(--mut)", fontWeight: x.anomaly ? 700 : 400 }}>
                  {x.score.toFixed(3)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="prow" style={{ padding: "16px 24px", borderTop: "1px solid var(--line)", fontSize: 14 }}>
        <span>Showing {v.length ? cur * PAGE_SIZE + 1 : 0} to {Math.min(v.length, cur * PAGE_SIZE + PAGE_SIZE)} of {v.length} records</span>
        <div className="ml">
          <button className="pill" disabled={cur === 0} onClick={() => setPg(cur - 1)}>‹</button>
          <b>Page {cur + 1} of {pages}</b>
          <button className="pill" disabled={cur >= pages - 1} onClick={() => setPg(cur + 1)}>›</button>
        </div>
      </div>
    </section>
  );
};
