/**
 * Thin fetch wrapper around the backend API. This is the ONLY file that
 * knows about HTTP endpoints - components just call these functions.
 * The frontend never talks to the ML layer directly (Frontend -> Backend
 * API -> ML Inference -> Backend -> Frontend).
 */
const API_BASE = "http://127.0.0.1:8000"; // same-origin; change if the backend is hosted elsewhere

function toApiParams(p) {
  return {
    seed: p.seed, n: p.n,
    spike: p.spike, spike_t: p.spikeT, spike_h: p.spikeH,
    frozen: p.frozen, frozen_d: p.frozenD, frozen_h: p.frozenH,
    drift: p.drift, drift_d: p.driftD, drift_h: p.driftH,
    contam: p.contam,
  };
}

const Api = {
  async fetchTelemetry(p) {
    const res = await fetch(`${API_BASE}/api/telemetry`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(toApiParams(p)),
    });
    if (!res.ok) throw new Error(`Telemetry request failed: ${res.status}`);
    return res.json(); // { params, kpis, rows, run_id }
  },

  async downloadCsv(p) {
    const res = await fetch(`${API_BASE}/api/telemetry/csv`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(toApiParams(p)),
    });
    if (!res.ok) throw new Error(`CSV export failed: ${res.status}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "skyguard_sensor_telemetry.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  },
};
