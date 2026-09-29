# SkyGuard AI — Restructured Project

A production-style restructuring of the SkyGuard AI sensor-anomaly dashboard
prototype. **The UI, layout, colors, fonts, spacing, icons, tabs, charts,
interactions, copy and behavior are unchanged.** Only the code organization
changed: the single-file prototype is now split into `frontend/`, `backend/`,
`ml/` and a real database layer, communicating over a REST API.

```
Frontend (React, static files)
   │  fetch() JSON over HTTP
   ▼
Backend (FastAPI: routes → controllers → services)
   │  in-process function call
   ▼
ML layer (ml/inference.py → preprocessing → prediction)
   │  reads/writes
   ▼
Database (SQLAlchemy → SQLite by default)
```

---

## 1. Prototype analysis (before restructuring)

**Technologies used:** a single self-contained `skyguard.html` file — React 18
+ Babel Standalone loaded from a CDN (no build step), plain CSS, and a
hand-written JavaScript re-implementation of an Isolation Forest and a
rule-based fault classifier (because real scikit-learn can't run in a
browser). The original design reference was a Python/Streamlit script
(`app.py`) using pandas, scikit-learn's `IsolationForest` and
`RandomForestClassifier`, and Plotly.

**Main features:**
- Synthetic hourly weather telemetry generator (temperature, humidity,
  pressure) with a seeded RNG and three injectable hardware faults: a
  temperature **spike**, **frozen** humidity, and pressure **drift**.
- Feature engineering: first-order differences, rolling std/mean, deviation
  from a rolling baseline.
- Anomaly detection via **Isolation Forest** (`contamination` slider).
- Fault-type classification via a **Random Forest**-equivalent classifier.
- KPI cards, a tabbed interactive chart (Temperature / Humidity / Pressure /
  Combined) with hover tooltips and red anomaly markers, a filterable +
  searchable + paginated diagnostic log, CSV export, and a fault-injection
  parameter panel with live sliders.

**Pages/screens (tabs):** Interactive Telemetry, app.py (reference code),
Pipeline Docs.

**APIs:** none — everything ran client-side in the browser.

**Database/data handling:** none — data was generated and discarded on every
render; nothing was persisted.

**Important components:** `Header`, `Hero`, `Kpis`, `Params`, `Chart`,
`Telemetry`, `Log`, `Docs`, `AppPy`, plus the pure functions `generate`,
`features`, `isoForest`, `runPipeline`.

---

## 2. Folder structure

```
skyguard-ai/
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── utils.js            # shared constants/helpers + hook destructuring
│       ├── api.js              # the ONLY file that calls the backend
│       └── components/
│           ├── Header.js  Hero.js  Kpis.js  Params.js
│           ├── Chart.js  Telemetry.js  Log.js
│           └── Docs.js  AppPyView.js
│       (App.js ties it all together)
│
├── backend/
│   ├── main.py                 # FastAPI app + static frontend hosting
│   ├── routes/telemetry.py     # HTTP endpoints
│   ├── controllers/telemetry_controller.py
│   ├── services/telemetry_service.py   # calls ml/ + the database
│   ├── models/schemas.py       # Pydantic request/response models
│   ├── database/
│   │   ├── connection.py       # SQLAlchemy engine/session
│   │   ├── models.py           # ORM tables
│   │   └── seed.py             # create_all() / table setup
│   └── utils/config.py         # reads .env
│
├── ml/
│   ├── datasets/generate_synthetic.py   # ported generate_weather_data()
│   ├── preprocessing/features.py        # ported extract_sensor_features()
│   ├── training/train.py                # trains + saves the default models
│   ├── prediction/predict.py            # loads/fits models, runs predictions
│   ├── models/                          # isolation_forest.pkl, random_forest.pkl (generated)
│   └── inference.py             # the one function the backend calls
│
├── .env / .env.example
├── requirements.txt
├── README.md
└── .gitignore
```

## 3. Mapping: prototype → new files

| Original prototype code                              | New location |
|--------------------------------------------------------|--------------|
| `<style>` block                                        | `frontend/css/style.css` |
| `App` component + `ReactDOM.render`                     | `frontend/js/App.js` |
| `Header`, `Hero`, `Kpis`, `Params`, `Chart`, `Telemetry`, `Log`, `Docs`, `AppPy` | `frontend/js/components/*.js` |
| `DEF`, `fmt`, `VIEWS`, `domain`, `TIPC`, `ICON`, `PAGE`  | `frontend/js/utils.js` |
| JS `generate()` (data synthesis)                         | `ml/datasets/generate_synthetic.py` (now the real, original Python/NumPy version) |
| JS `features()`                                          | `ml/preprocessing/features.py` |
| JS `isoForest()` + rule-based `runPipeline()` classifier  | `ml/prediction/predict.py` (now the **real** `sklearn.IsolationForest` + `RandomForestClassifier` from `app.py`, not the JS approximation) |
| — (no backend existed)                                   | `backend/main.py`, `backend/routes/telemetry.py`, `backend/controllers/`, `backend/services/` |
| — (no persistence existed)                               | `backend/database/models.py`, `connection.py`, `seed.py` |
| `window.claude.use("downloads")` CSV export               | `POST /api/telemetry/csv` + `frontend/js/api.js` (`Api.downloadCsv`) |

**Note on the ML swap:** the original HTML prototype used a hand-rolled JS
Isolation Forest and a small set of if/else rules standing in for the Random
Forest, because real scikit-learn cannot run in a browser. Now that there is
a real Python backend, `ml/` runs the **actual algorithms from the original
`app.py`** (`sklearn.ensemble.IsolationForest` and `RandomForestClassifier`,
same features, same hyperparameters) — this is strictly more faithful to
"the exact same functionality," not a redesign.

---

## 4. Machine learning workflow

```
ml/
├── datasets/generate_synthetic.py   # 1. synthetic telemetry + fault injection
├── preprocessing/features.py        # 1. feature engineering
├── training/train.py                # 2. trains + evaluates + saves models
├── models/                          # 3. persisted isolation_forest.pkl / random_forest.pkl
├── prediction/predict.py            # 4. loads model, accepts data, returns predictions
└── inference.py                     # single clean entrypoint for the backend
```

`backend/services/telemetry_service.py` is the only backend file that
imports `ml.inference` — the frontend never talks to the ML layer directly:

```
Frontend → Backend API → ML Inference → Prediction → Backend → Frontend
```

**Important trade-off, stated plainly:** this app is a live simulator — the
sidebar lets you change the random seed, the fault-injection parameters and
the Isolation Forest `contamination` rate, which changes the dataset itself
and the correct ground-truth labels. That was true of the original
Streamlit prototype too: it refit both models on every rerun. To preserve
that exact behavior:
- `ml/training/train.py` trains **once** and persists `isolation_forest.pkl`
  and `random_forest.pkl` for the default configuration (seed 42, 500 rows,
  default faults, contamination 0.08).
- `ml/prediction/predict.py` loads those persisted models as a fast path
  whenever a request matches that default configuration exactly, and
  otherwise fits both models live on the requested configuration (cached
  per parameter set for the life of the process) — exactly what the
  original prototype did. No algorithm, feature, or hyperparameter was
  changed either way.

No dummy predictions are used anywhere; no preprocessing steps were removed.

---

## 5. Setup & install

```bash
cd skyguard-ai
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # already done in this delivered copy
```

### .env requirements
See `.env.example` — `DATABASE_URL` (SQLite by default, no setup needed),
`CORS_ORIGINS`, `DEFAULT_SEED`/`DEFAULT_CONTAMINATION` (must match
`ml/training/train.py` if you change either), `HOST`/`PORT`. There are no
external API keys required by this app.

### Database setup
SQLite needs no separate install. Tables are created automatically on
backend startup, or manually:
```bash
python -m backend.database.seed
```

### Train the default ML models (recommended, one-time)
```bash
python -m ml.training.train
```
This writes `ml/models/isolation_forest.pkl` and `random_forest.pkl`. If you
skip this step, the backend still works — it just fits fresh models on every
non-default request, same as the original prototype's live behavior.

### Run the backend (also serves the frontend)
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
Open **http://localhost:8000** — this serves `frontend/index.html` and the
`/api/*` JSON endpoints from the same process.

### Run the frontend separately (optional)
The frontend is static files with no build step, so you can also serve it on
its own, e.g.:
```bash
cd frontend
python -m http.server 5500
```
Then open http://localhost:5500 — just make sure `CORS_ORIGINS` in `.env`
includes `http://localhost:5500` and `API_BASE` in `frontend/js/api.js`
points at `http://localhost:8000` if the two are on different ports.

---

## 6. API endpoints

| Method | Path                | Description |
|--------|---------------------|--------------|
| GET    | `/api/health`        | Health check |
| POST   | `/api/telemetry`     | Runs the full ML pipeline for the given params, stores the run, returns `{ params, kpis, rows, run_id }` |
| POST   | `/api/telemetry/csv` | Same pipeline, returns a downloadable CSV file |
| GET    | `/api/runs?limit=25` | History of previously generated/stored simulation runs |

Request body for the two `POST` endpoints (`GenerateParams`):
```json
{
  "seed": 42, "n": 500,
  "spike": true, "spike_t": 95.0, "spike_h": 120,
  "frozen": true, "frozen_d": 15, "frozen_h": 240,
  "drift": true, "drift_d": 30, "drift_h": 360,
  "contam": 0.08
}
```

## 7. How the pieces talk to each other

1. The frontend (`js/App.js`) holds the sidebar parameters in state and
   calls `Api.fetchTelemetry(params)` (`frontend/js/api.js`) whenever they
   change.
2. That hits `POST /api/telemetry` (`backend/routes/telemetry.py`), which
   calls `telemetry_controller.generate_telemetry`.
3. The controller calls `telemetry_service.generate_and_store`
   (`backend/services/telemetry_service.py`), which calls
   `ml.inference.run_pipeline(...)` — the one function the backend is
   allowed to call into `ml/`.
4. `ml/inference.py` generates the synthetic dataset, engineers features,
   and runs the Isolation Forest + Random Forest pipeline
   (`ml/prediction/predict.py`), returning a pandas DataFrame.
5. The service converts that DataFrame into JSON-ready rows, computes the
   KPI summary, and persists both the run and its rows via SQLAlchemy
   (`backend/database/models.py`) into SQLite.
6. The controller wraps the result in the `TelemetryResponse` schema and the
   route returns it as JSON.
7. The frontend renders the same KPI cards, charts and log it always did —
   just fed by the backend response instead of an in-browser computation.
