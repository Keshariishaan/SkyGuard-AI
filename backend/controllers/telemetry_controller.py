"""
Controllers format service-layer results into API response shapes.
Routes stay thin; they just wire HTTP verbs/paths to these functions.
"""

from sqlalchemy.orm import Session

from backend.models.schemas import GenerateParams, TelemetryResponse
from backend.services import telemetry_service


def generate_telemetry(params: GenerateParams, db: Session) -> TelemetryResponse:
    result = telemetry_service.generate_and_store(params, db)
    return TelemetryResponse(**result)


def export_csv(params: GenerateParams, db: Session) -> str:
    result = telemetry_service.generate_and_store(params, db)
    return telemetry_service.rows_to_csv(result["rows"])


def get_run_history(db: Session, limit: int = 25):
    runs = telemetry_service.list_runs(db, limit)
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "seed": r.seed,
            "n_hours": r.n_hours,
            "contamination": r.contamination,
            "total_anomalies": r.total_anomalies,
            "spike_count": r.spike_count,
            "frozen_count": r.frozen_count,
            "drift_count": r.drift_count,
        }
        for r in runs
    ]
