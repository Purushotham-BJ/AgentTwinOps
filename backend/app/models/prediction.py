"""Persisted prediction execution history."""
from datetime import datetime, timezone
import uuid
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("infrastructure.id", ondelete="CASCADE"), nullable=False, index=True)
    prediction_type: Mapped[str] = mapped_column(String(16), nullable=False)
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    failure_probability: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    factors: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default="[]")
    recommended_action: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    horizon_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    historical_metrics: Mapped[list[float]] = mapped_column(JSONB, nullable=False, server_default="[]")
    model_metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")
    prediction_source: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
