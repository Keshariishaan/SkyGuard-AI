from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.controllers import telemetry_controller
from backend.database.connection import get_db
from backend.models.schemas import GenerateParams, RunSummary, TelemetryResponse

router = APIRouter(prefix="/api", tags=["telemetry"])


@router.post("/telemetry", response_model=TelemetryResponse)
def generate_telemetry(params: GenerateParams, db: Session = Depends(get_db)):
    """
    Runs the full pipeline (data generation -> feature engineering ->
    Isolation Forest -> Random Forest) for the given simulation
    parameters and returns the rows + KPI summary the dashboard needs.
    """
    return telemetry_controller.generate_telemetry(params, db)


@router.post("/telemetry/csv")
def export_telemetry_csv(params: GenerateParams, db: Session = Depends(get_db)):
    """Same pipeline as /api/telemetry, returned as a downloadable CSV file."""
    csv_text = telemetry_controller.export_csv(params, db)
    return StreamingResponse(
        iter([csv_text]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=skyguard_sensor_telemetry.csv"},
    )


@router.get("/runs", response_model=list[RunSummary])
def get_runs(limit: int = 25, db: Session = Depends(get_db)):
    """History of previously generated/stored simulation runs."""
    return telemetry_controller.get_run_history(db, limit)
