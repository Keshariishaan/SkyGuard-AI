function App() {
  const [tab, setTab] = useState("tel");
  const [p, setP] = useState(DEF);
  const [data, setData] = useState(null); // { params, kpis, rows, run_id }
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    Api.fetchTelemetry(p)
      .then((res) => { if (!cancelled) setData(res); })
      .catch((err) => { if (!cancelled) setError(err.message || "Failed to load telemetry"); });
    return () => { cancelled = true; };
  }, [p]);

  return (
    <>
      <Header tab={tab} setTab={setTab} />
      <main className="wrap">
        {tab === "tel" && (
          <>
            <Hero go={() => setTab("app")} />
            {error && (
              <section className="panel" style={{ borderColor: "#fecaca", color: "#b91c1c" }}>
                Could not reach the backend API: {error}. Is <code>uvicorn backend.main:app</code> running?
              </section>
            )}
            {!data && !error && <section className="panel">Generating telemetry…</section>}
            {data && (
              <>
                <Kpis kpis={data.kpis} />
                <Params p={p} set={setP} />
                <Telemetry rows={data.rows} p={p} />
                <Log rows={data.rows} p={p} />
              </>
            )}
          </>
        )}
        {tab === "app" && <AppPyView />}
        {tab === "docs" && data && <Docs p={p} />}
      </main>
    </>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
