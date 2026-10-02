"""Persisted simulation execution history."""
from datetime import datetime
import uuid
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SimulationHistory(Base):
    __tablename__ = "simulation_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("infrastructure.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    baseline_state: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    scenario_changes: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    simulated_state: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    simulated_health_score: Mapped[float] = mapped_column(Float, nullable=False)
    simulated_failure_probability: Mapped[float] = mapped_column(Float, nullable=False)
    simulated_operational_status: Mapped[str] = mapped_column(String(32), nullable=False)
    impact_summary: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    predicted_impact: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    recommendations: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
