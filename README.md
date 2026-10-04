# SkyGuard AI

**Anomaly detection and fault diagnosis for weather-station sensor telemetry.**

SkyGuard AI is a full-stack dashboard that simulates hourly weather telemetry (temperature, humidity, pressure), injects realistic hardware faults, and uses machine learning to detect and classify them. It pairs a React frontend with a FastAPI backend, a scikit-learn ML layer, and a SQLAlchemy-backed database.

> **Notice: not for commercial use.** This repository is a prototype built for learning and educational purposes only. It may not be used in commercial products, services, or for any commercial gain.

## Features

- **Synthetic telemetry generator**: seeded, reproducible hourly data with three injectable sensor faults:
  - temperature **spikes**
  - **frozen** humidity readings
  - pressure **drift**
- **Feature engineering**: first-order differences, rolling mean and standard deviation, and deviation from a rolling baseline.
- **Anomaly detection**: scikit-learn `IsolationForest` with an adjustable `contamination` rate.
- **Fault classification**: scikit-learn `RandomForestClassifier` that labels the type of fault detected.
- **Interactive dashboard**:
  - KPI cards
  - tabbed charts (Temperature, Humidity, Pressure, Combined) with hover tooltips and anomaly markers
  - a searchable, filterable, paginated diagnostic log
  - live parameter sliders
  - CSV export
- **Run history**: every simulation run is stored in the database and can be retrieved later.

## Architecture

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

The frontend never talks to the ML layer directly. `backend/services/telemetry_service.py` is the only backend module that imports `ml.inference`.

## Tech Stack

| Layer     | Technologies |
|-----------|--------------|
| Frontend  | React 18 (loaded via CDN, no build step), plain CSS |
| Backend   | FastAPI, Pydantic, Uvicorn |
| ML        | Python, NumPy, pandas, scikit-learn |
| Database  | SQLAlchemy (SQLite by default) |

## Project Structure

```
skyguard-ai/
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── utils.js            # shared constants and helpers
│       ├── api.js              # the only file that calls the backend
│       ├── App.js              # ties the components together
│       └── components/
│           ├── Header.js  Hero.js  Kpis.js  Params.js
│           ├── Chart.js  Telemetry.js  Log.js
│           └── Docs.js  AppPyView.js
│
├── backend/
│   ├── main.py                 # FastAPI app + static frontend hosting
│   ├── routes/telemetry.py     # HTTP endpoints
│   ├── controllers/telemetry_controller.py
│   ├── services/telemetry_service.py   # calls ml/ and the database
│   ├── models/schemas.py       # Pydantic request/response models
│   ├── database/
│   │   ├── connection.py       # SQLAlchemy engine/session
│   │   ├── models.py           # ORM tables
│   │   └── seed.py             # table creation
│   └── utils/config.py         # reads .env
│
├── ml/
│   ├── datasets/generate_synthetic.py   # synthetic telemetry + fault injection
│   ├── preprocessing/features.py        # feature engineering
│   ├── training/train.py                # trains and saves the default models
│   ├── prediction/predict.py            # loads/fits models, runs predictions
│   ├── models/                          # generated .pkl files
│   └── inference.py                     # single entrypoint used by the backend
│
├── .env.example
├── requirements.txt
└── README.md
```

## Machine Learning Workflow

1. **Data generation**: `ml/datasets/generate_synthetic.py` creates seeded telemetry and injects the configured faults.
2. **Preprocessing**: `ml/preprocessing/features.py` computes the engineered features.
3. **Training**: `ml/training/train.py` trains and saves `isolation_forest.pkl` and `random_forest.pkl` for the default configuration.
4. **Prediction**: `ml/prediction/predict.py` loads a model, accepts data, and returns predictions.
5. **Inference**: `ml/inference.py` is the one function the backend calls.

**A note on training vs. live fitting.** SkyGuard is a live simulator: changing the seed, the fault parameters, or the `contamination` rate changes the dataset and its ground-truth labels, so a single pre-trained model can't serve every request. To handle this:

- The persisted models cover the default configuration (seed `42`, 500 rows, default faults, contamination `0.08`) and are used as a fast path when a request matches it exactly.
- For any other configuration, both models are fit live on the requested data and cached per parameter set for the life of the process.

## Getting Started

### Prerequisites

- Python 3.9+

### Installation

```bash
git clone <your-repo-url>
cd skyguard-ai
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### Configuration

Edit `.env` as needed (defaults work out of the box):

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Database connection string (SQLite by default, no setup needed) |
| `CORS_ORIGINS` | Allowed origins if the frontend is served separately |
| `DEFAULT_SEED`, `DEFAULT_CONTAMINATION` | Defaults for the pre-trained models; must match `ml/training/train.py` if you change either |
| `HOST`, `PORT` | Server bind address |

No external API keys are required.

### Database

Tables are created automatically when the backend starts. To create them manually:

```bash
python -m backend.database.seed
```

### Train the default models (optional, recommended)

```bash
python -m ml.training.train
```

This writes `ml/models/isolation_forest.pkl` and `ml/models/random_forest.pkl`. If you skip this step, the backend still works and fits fresh models for each non-default request.

### Run the app

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000**. The backend serves both the frontend and the `/api/*` endpoints.

### Running the frontend separately (optional)

The frontend is static, so you can serve it on its own:

```bash
cd frontend
python -m http.server 5500
```

Then open http://localhost:5500. Make sure `CORS_ORIGINS` in `.env` includes `http://localhost:5500`, and set `API_BASE` in `frontend/js/api.js` to `http://localhost:8000`.

## API Reference

| Method | Path                 | Description |
|--------|----------------------|-------------|
| GET    | `/api/health`        | Health check |
| POST   | `/api/telemetry`     | Runs the ML pipeline, stores the run, returns `{ params, kpis, rows, run_id }` |
| POST   | `/api/telemetry/csv` | Runs the same pipeline and returns a downloadable CSV |
| GET    | `/api/runs?limit=25` | Lists previously stored simulation runs |

**Request body** for the `POST` endpoints:

```json
{
  "seed": 42, "n": 500,
  "spike": true, "spike_t": 95.0, "spike_h": 120,
  "frozen": true, "frozen_d": 15, "frozen_h": 240,
  "drift": true, "drift_d": 30, "drift_h": 360,
  "contam": 0.08
}
```

## How a Request Flows

1. The frontend (`js/App.js`) keeps the sidebar parameters in state and calls `Api.fetchTelemetry(params)` whenever they change.
2. The call hits `POST /api/telemetry`, which delegates to `telemetry_controller.generate_telemetry`.
3. The controller calls `telemetry_service.generate_and_store`, which in turn calls `ml.inference.run_pipeline(...)`.
4. The ML layer generates the dataset, engineers features, and runs the Isolation Forest and Random Forest pipeline, returning a pandas DataFrame.
5. The service converts the DataFrame to JSON-ready rows, computes the KPI summary, and persists the run and its rows to the database.
6. The controller wraps everything in the `TelemetryResponse` schema and the route returns it as JSON.
7. The frontend renders the KPI cards, charts, and diagnostic log from the response.

## Contributing

Issues and pull requests are welcome. For larger changes, please open an issue first to discuss what you'd like to change.
