const Slider = ({ label, k, min, max, step = 1, p, set, fmt = (v) => v }) => (
  <label>{label}: <b>{fmt(p[k])}</b>
    <input type="range" min={min} max={max} step={step} value={p[k]} onChange={(e) => set({ ...p, [k]: +e.target.value })} />
  </label>
);
const Check = ({ label, k, p, set }) => (
  <label><input type="checkbox" checked={p[k]} onChange={(e) => set({ ...p, [k]: e.target.checked })} /> <b>{label}</b></label>
);

const Params = ({ p, set }) => {
  const [open, setOpen] = useState(false);
  return (
    <section className="panel">
      <div className="prow">
        <div className="logo" style={{ width: 40, height: 40, background: "var(--chip)", color: "var(--ink)", fontSize: 16 }}>⫶</div>
        <div>
          <div className="t">Synthetic Sensor &amp; Fault Injection Parameters</div>
          <div className="s">{p.n} rows simulated hourly data with calibrated anomaly injection</div>
        </div>
        <div className="ml">
          <button className="pill" onClick={() => setOpen(!open)}>Tune Fault Injections</button>
          <button className="pill" onClick={() => set({ ...p, seed: 1 + Math.floor(Math.random() * 9999) })}>New Random Seed (#{p.seed})</button>
          <button className="pill" title="Reset" onClick={() => set(DEF)}>↻</button>
        </div>
      </div>
      {open && (
        <div className="sl">
          <Slider label="Dataset rows (hours)" k="n" min={200} max={1000} step={50} p={p} set={set} />
          <Slider label="Isolation Forest contamination" k="contam" min={0.01} max={0.15} step={0.01} p={p} set={set} />
          <div>
            <Check label="Inject temperature spike" k="spike" p={p} set={set} />
            <Slider label="Spike °C" k="spikeT" min={50} max={120} p={p} set={set} />
            <Slider label="Spike hour" k="spikeH" min={10} max={p.n - 10} p={p} set={set} />
          </div>
          <div>
            <Check label="Inject frozen humidity" k="frozen" p={p} set={set} />
            <Slider label="Duration (h)" k="frozenD" min={5} max={40} p={p} set={set} />
            <Slider label="Start hour" k="frozenH" min={10} max={p.n - 50} p={p} set={set} />
          </div>
          <div>
            <Check label="Inject pressure drift" k="drift" p={p} set={set} />
            <Slider label="Duration (h)" k="driftD" min={10} max={60} step={5} p={p} set={set} />
            <Slider label="Start hour" k="driftH" min={10} max={p.n - 70} p={p} set={set} />
          </div>
        </div>
      )}
    </section>
  );
};
