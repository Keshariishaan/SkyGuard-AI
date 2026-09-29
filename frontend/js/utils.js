/**
 * Small shared helpers used across components.
 *
 * React hooks are destructured ONCE here (top-level `const` declarations
 * are shared across every <script> tag on the page, so redeclaring them
 * in each component file would throw a "already declared" error).
 */
const { useState, useEffect, useMemo, useRef } = React;

const DEF = {
  seed: 42, n: 500,
  spike: true, spikeT: 95, spikeH: 120,
  frozen: true, frozenD: 15, frozenH: 240,
  drift: true, driftD: 30, driftH: 360,
  contam: 0.10,
};

// Backend already returns "YYYY-MM-DDTHH:MM:SS" - just reformat the string.
const fmt = (ts) => ts.slice(0, 16).replace("T", " ");

const VIEWS = {
  temperature: [["temperature", "Temperature", "#c2410c", "°C", "L"]],
  humidity: [["humidity", "Humidity", "#4a90b0", "%", "L"]],
  pressure: [["pressure", "Pressure", "#6366f1", " hPa", "L"]],
  combined: [
    ["temperature", "Temperature (°C)", "#c2410c", "°C", "L"],
    ["humidity", "Humidity (%)", "#4a90b0", "%", "R"],
  ],
};

function domain(rows, k, view) {
  const v = rows.map((x) => x[k]), mn = Math.min(...v), mx = Math.max(...v);
  if (k === "temperature") return [0, Math.ceil((mx + (view === "temperature" ? 10 : 3)) / 10) * 10];
  if (k === "humidity") return [view === "humidity" ? 15 : 0, 100];
  return [Math.floor(mn) - 2, Math.ceil(mx) + 2];
}

const TIPC = { temperature: "#f59e0b", humidity: "#22d3ee", pressure: "#a78bfa" };
const ICON = { Normal: "✓", Spike: "ϟ", Frozen: "❄", Drift: "↗" };
const PAGE_SIZE = 12;
