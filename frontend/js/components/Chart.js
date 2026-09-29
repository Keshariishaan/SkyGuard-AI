const Chart = ({ rows, view, marks }) => {
  const ref = useRef(), [hv, setHv] = useState(null), lines = VIEWS[view], comb = view === "combined";
  const W = 1000, H = 340, L = 60, R = comb ? 60 : 16, T = 14, B = 34, n = rows.length;
  const dm = lines.map((l) => domain(rows, l[0], view));
  const X = (i) => L + (i / (n - 1)) * (W - L - R);
  const Y = (j, v) => T + (1 - (v - dm[j][0]) / (dm[j][1] - dm[j][0])) * (H - T - B);
  const tk = (j) => [0, 1, 2, 3, 4].map((i) => dm[j][0] + ((dm[j][1] - dm[j][0]) * i) / 4);
  const xt = []; for (let i = 0; i < n; i += 50) xt.push(i);
  const move = (e) => {
    const b = ref.current.getBoundingClientRect();
    setHv(Math.max(0, Math.min(n - 1, Math.round((((e.clientX - b.left) / b.width) * W - L) / (W - L - R) * (n - 1)))));
  };
  const hr = hv != null && rows[hv];

  return (
    <div>
      {comb && (
        <div style={{ textAlign: "center", fontSize: 17, marginTop: 6 }}>
          {[...lines].reverse().map((l) => <span key={l[0]} style={{ color: l[2], margin: "0 8px" }}>{l[1]}</span>)}
        </div>
      )}
      <div className="cw" ref={ref} onMouseMove={move} onMouseLeave={() => setHv(null)}>
        <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={view + " telemetry chart"}>
          <line x1={L} x2={L} y1={T} y2={H - B} stroke="var(--mut)" />
          <line x1={L} x2={W - R} y1={H - B} y2={H - B} stroke="var(--mut)" />
          {lines.map((l, j) => tk(j).map((v, i) => (
            <g key={j + "-" + i}>
              {j === 0 && <line x1={L} x2={W - R} y1={Y(j, v)} y2={Y(j, v)} stroke="var(--grid)" strokeDasharray="4 4" />}
              <text x={j ? W - R + 8 : L - 8} y={Y(j, v) + 4} textAnchor={j ? "start" : "end"} fontSize="12" fill={comb ? l[2] : "var(--mut)"}>
                {Math.round(v)}{l[3].trim()}
              </text>
            </g>
          )))}
          {xt.map((i) => <text key={i} x={X(i)} y={H - 12} textAnchor="middle" fontSize="12" fill="var(--mut)">H{i}</text>)}
          {lines.map((l, j) => (
            <polyline key={l[0]} fill="none" stroke={l[2]} strokeWidth="2" strokeLinejoin="round"
              points={rows.map((x, i) => X(i) + "," + Y(j, x[l[0]])).join(" ")} />
          ))}
          {marks && rows.map((x, i) => x.anomaly && lines.map((l, j) => (
            <g key={i + "-" + j}>
              <circle cx={X(i)} cy={Y(j, x[l[0]])} r="8" fill="#dc2626" fillOpacity=".18" />
              <circle cx={X(i)} cy={Y(j, x[l[0]])} r="5" fill="#c0392b" stroke="#fff" strokeWidth="1.5" />
            </g>
          )))}
          {hr && (
            <>
              <line x1={X(hv)} x2={X(hv)} y1={T} y2={H - B} stroke="var(--mut)" strokeOpacity=".6" />
              {lines.map((l, j) => <circle key={j} cx={X(hv)} cy={Y(j, hr[l[0]])} r="4.5" fill={l[2]} stroke="#fff" strokeWidth="1.5" />)}
            </>
          )}
        </svg>
        {hr && (
          <div className="tip" style={{ left: (X(hv) / W) * 100 + "%", transform: hv > n * 0.6 ? "translateX(-108%)" : "translateX(8%)" }}>
            <div className="th"><span>Hour #{hr.h}</span><span>{fmt(hr.ts)}</span></div>
            {[["temperature", "Temperature", "°C"], ["humidity", "Humidity", "%"], ["pressure", "Pressure", " hPa"]].map(([k, l, u]) => (
              <div className="tr" key={k}><span style={{ color: TIPC[k] }}>{l}:</span><b>{hr[k]}{u}</b></div>
            ))}
            <div style={{ color: hr.anomaly ? "#f87171" : "#34d399", marginTop: 8 }}>
              ● {hr.anomaly ? "Anomaly · " + hr.diagnosis : "Nominal telemetry reading"}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
