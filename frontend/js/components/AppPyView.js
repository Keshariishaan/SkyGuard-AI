const AppPyView = () => (
  <section className="panel">
    <h3 style={{ margin: "0 0 6px", fontSize: 22 }}>app.py (Streamlit) — key pipeline</h3>
    <div className="sub" style={{ marginBottom: 12 }}>
      This is the same pipeline the backend's ml/ layer now runs (ml/prediction/predict.py), ported from the original Streamlit prototype.
    </div>
    <pre>{`iso_model = IsolationForest(contamination=0.08, random_state=42, n_estimators=150)
df["is_anomaly"] = iso_model.fit_predict(features_df[["temperature","humidity","pressure"]]) == -1

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(features_df[clf_feature_cols], df["ground_truth"])
df["final_diagnosis"] = np.where(df["is_anomaly"], rf.predict(features_df[clf_feature_cols]), "Normal")`}</pre>
  </section>
);
