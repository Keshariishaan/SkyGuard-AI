"""
Business logic. This is the ONLY layer that talks to ml/ and to the
database - controllers/routes never import ml or SQLAlchemy directly.

Flow: Frontend -> Backend API (routes) -> Controller -> Service (here)
      -> ML inference -> Service stores in DB -> Controller -> Frontend
"""

import io
from typing import List

import pandas as pd
from sqlalchemy.orm import Session

from backend.database.models import TelemetryPoint, TelemetryRun
from backend.models.schemas import GenerateParams
from ml.inference import run_pipeline


def _to_row_dicts(df: pd.DataFrame) -> List[dict]:
    return [
        {
            "h": int(r.hour_index),
            "ts": r.timestamp.isoformat(),
            "temperature": float(r.temperature),
            "humidity": float(r.humidity),
            "pressure": float(r.pressure),
            "anomaly": bool(r.is_anomaly),
            "diagnosis": str(r.final_diagnosis),
            "truth": str(r.ground_truth),
            "score": round(float(r.anomaly_score), 3),
        }
        for r in df.itertuples()
    ]


def _kpis(rows: List[dict]) -> dict:
    anomalies = [r for r in rows if r["anomaly"]]
    return {
        "total": len(rows),
        "anomalies": len(anomalies),
        "spike": len([r for r in anomalies if r["diagnosis"] == "Spike"]),
        "frozen": len([r for r in anomalies if r["diagnosis"] == "Frozen"]),
        "drift": len([r for r in anomalies if r["diagnosis"] == "Drift"]),
    }


def generate_and_store(params: GenerateParams, db: Session) -> dict:
    """Runs the ML pipeline, persists the run + rows, returns API-ready dict."""
    df = run_pipeline(
        rows=params.n,
        seed=params.seed,
        spike_en=params.spike, spike_t=params.spike_t, spike_idx=params.spike_h,
        frozen_en=params.frozen, frozen_dur=params.frozen_d, frozen_idx=params.frozen_h,
        drift_en=params.drift, drift_dur=params.drift_d, drift_idx=params.drift_h,
        contamination=params.contam,
    )

    rows = _to_row_dicts(df)
    kpis = _kpis(rows)

    run = TelemetryRun(
        seed=params.seed, n_hours=params.n,
        spike_enabled=params.spike, spike_temp=params.spike_t, spike_hour=params.spike_h,
        frozen_enabled=params.frozen, frozen_duration=params.frozen_d, frozen_hour=params.frozen_h,
        drift_enabled=params.drift, drift_duration=params.drift_d, drift_hour=params.drift_h,
        contamination=params.contam,
        total_points=kpis["total"], total_anomalies=kpis["anomalies"],
        spike_count=kpis["spike"], frozen_count=kpis["frozen"], drift_count=kpis["drift"],
    )
    db.add(run)
    db.flush()  # get run.id before inserting points

    db.bulk_save_objects([
        TelemetryPoint(
            run_id=run.id,
            hour_index=r["h"],
            timestamp=pd.to_datetime(r["ts"]),
            temperature=r["temperature"], humidity=r["humidity"], pressure=r["pressure"],
            is_anomaly=r["anomaly"], final_diagnosis=r["diagnosis"],
            ground_truth=r["truth"], anomaly_score=r["score"],
        )
        for r in rows
    ])
    db.commit()

    return {"params": params, "kpis": kpis, "rows": rows, "run_id": run.id}


def list_runs(db: Session, limit: int = 25) -> List[TelemetryRun]:
    return (
        db.query(TelemetryRun)
        .order_by(TelemetryRun.created_at.desc())
        .limit(limit)
        .all()
    )


def rows_to_csv(rows: List[dict]) -> str:
    buf = io.StringIO()
    buf.write("hour,timestamp,temperature,humidity,pressure,is_anomaly,final_diagnosis,ground_truth,anomaly_score\n")
    for r in rows:
        buf.write(
            f'{r["h"]},{r["ts"]},{r["temperature"]},{r["humidity"]},{r["pressure"]},'
            f'{r["anomaly"]},{r["diagnosis"]},{r["truth"]},{r["score"]}\n'
        )
    return buf.getvalue()
