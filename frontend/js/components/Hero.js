const Hero = ({ go }) => (
  <section className="hero"><div>
    <div className="st">◉ Prototype online — synthetic weather stream ingested</div>
    <h2>Weather Hardware Sensor Telemetry &amp; Anomaly Diagnostics</h2>
    <p>Ingesting hourly records of Temperature, Humidity, and Atmospheric Pressure. Sensors are monitored using an <b>Isolation Forest</b> algorithm to detect out-of-distribution points, while a <b>Random Forest Classifier</b> categorizes hardware failure modes into <i>Spikes</i>, <i>Frozen readings</i>, and <i>Barometric drift</i>.</p>
  </div><button className="go" onClick={go}>›_ View app.py</button></section>
);
