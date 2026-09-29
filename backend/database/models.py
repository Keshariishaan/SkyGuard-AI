"""
ORM schema.

The original prototype had no persistence layer at all - it recomputed
everything in memory on every render. This adds a thin persistence layer
(each generated run and its rows) purely so the project has a real
database tier, as required by the restructuring spec. It does not change
any visible UI behavior: the frontend still receives the same rows/kpis
shape it always did.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from backend.database.connection import Base


class TelemetryRun(Base):
    """One generated simulation (= one set of sidebar parameters)."""

    __tablename__ = "telemetry_runs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    seed = Column(Integer, nullable=False)
    n_hours = Column(Integer, nullable=False)

    spike_enabled = Column(Boolean, default=True)
    spike_temp = Column(Float, default=95.0)
    spike_hour = Column(Integer, default=120)

    frozen_enabled = Column(Boolean, default=True)
    frozen_duration = Column(Integer, default=15)
    frozen_hour = Column(Integer, default=240)

    drift_enabled = Column(Boolean, default=True)
    drift_duration = Column(Integer, default=30)
    drift_hour = Column(Integer, default=360)

    contamination = Column(Float, default=0.08)

    total_points = Column(Integer)
    total_anomalies = Column(Integer)
    spike_count = Column(Integer)
    frozen_count = Column(Integer)
    drift_count = Column(Integer)

    points = relationship(
        "TelemetryPoint", back_populates="run", cascade="all, delete-orphan"
    )


class TelemetryPoint(Base):
    """One hourly telemetry row belonging to a TelemetryRun."""

    __tablename__ = "telemetry_points"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("telemetry_runs.id"), nullable=False)

    hour_index = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)

    is_anomaly = Column(Boolean)
    final_diagnosis = Column(String)
    ground_truth = Column(String)
    anomaly_score = Column(Float)

    run = relationship("TelemetryRun", back_populates="points")
