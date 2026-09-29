"""
Pydantic models = the API contract between frontend and backend. Field
names/defaults mirror the original prototype's sidebar (DEF object in
the frontend JS) exactly - only naming style is snake_case for Python.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class GenerateParams(BaseModel):
    seed: int = Field(42, ge=1, le=9999)
    n: int = Field(500, ge=200, le=1000)

    spike: bool = True
    spike_t: float = Field(95.0, ge=50, le=120)
    spike_h: int = Field(120, ge=10)

    frozen: bool = True
    frozen_d: int = Field(15, ge=5, le=40)
    frozen_h: int = Field(240, ge=10)

    drift: bool = True
    drift_d: int = Field(30, ge=10, le=60)
    drift_h: int = Field(360, ge=10)

    contam: float = Field(0.08, ge=0.01, le=0.15)


class TelemetryPointOut(BaseModel):
    h: int
    ts: str
    temperature: float
    humidity: float
    pressure: float
    anomaly: bool
    diagnosis: str
    truth: str
    score: float


class Kpis(BaseModel):
    total: int
    anomalies: int
    spike: int
    frozen: int
    drift: int


class TelemetryResponse(BaseModel):
    params: GenerateParams
    kpis: Kpis
    rows: List[TelemetryPointOut]
    run_id: Optional[int] = None


class RunSummary(BaseModel):
    id: int
    created_at: str
    seed: int
    n_hours: int
    contamination: float
    total_anomalies: int
    spike_count: int
    frozen_count: int
    drift_count: int
