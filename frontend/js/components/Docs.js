const Docs = ({ p }) => (
  <section className="panel docs">
    <h2>SkyGuard AI Architecture &amp; Methodology</h2>
    <div className="sub" style={{ fontSize: 16 }}>
      A two-stage machine learning system designed to protect environmental and meteorological sensor arrays from hardware failure degradation.
    </div>
    <div className="cards">
      <div className="fc fa">
        <h4>● 1. Thermal Spike Fault</h4>
        <p><b>Symptom:</b> Sudden jump to {p.spikeT}°C for 1 hour at index ~{p.spikeH}.</p>
        <p><b>Physical cause:</b> Transient electrical surges, ADC short-circuit, or power supply spike.</p>
        <p><b>Detection:</b> Isolation Forest path isolation on high 1st-order temperature difference.</p>
      </div>
      <div className="fc fb">
        <h4>● 2. Frozen Sensor Fault</h4>
        <p><b>Symptom:</b> {p.frozenD} consecutive hours without humidity changing by even 0.01% at index ~{p.frozenH}.</p>
        <p><b>Physical cause:</b> Sensor communication bus deadlock, I2C freeze, or saturated transducer membrane.</p>
        <p><b>Detection:</b> Rolling standard deviation of 0.000 across multiple samples.</p>
      </div>
      <div className="fc fc3">
        <h4>● 3. Barometric Drift Fault</h4>
        <p><b>Symptom:</b> Pressure values slowly creeping upward incorrectly over {p.driftD} hours at index ~{p.driftH}.</p>
        <p><b>Physical cause:</b> Piezoelectric sensor aging, diaphragm micro-leak, or temperature compensation drift.</p>
        <p><b>Detection:</b> Deviation from synoptic atmospheric pressure baseline trend.</p>
      </div>
    </div>
    <h3 style={{ margin: "0 0 12px" }}>Model Pipeline Workflow</h3>
    <pre>{`Step 1: Raw Telemetry (${p.n} rows) → Feature Engineering (differences, rolling standard deviation, baseline deviations).
Step 2: IsolationForest(contamination=${p.contam}, n_estimators=150) → flags anomalous points (-1 anomaly, 1 normal).
Step 3: RandomForestClassifier(n_estimators=100) → labels diagnosed failure category: Normal | Spike | Frozen | Drift.
Step 4: React Dashboard (frontend) renders time-series lines with red alert markers on anomalous points, fed by the FastAPI backend.`}</pre>
  </section>
);
