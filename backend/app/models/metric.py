"""Metric ORM model for AgentTwinOps."""

from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.infrastructure import Infrastructure


class Metric(Base):
    """Metric model representing telemetry data.
    
    Maps to the metrics table in PostgreSQL.
    """

    __tablename__ = "metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("infrastructure.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    cpu_usage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    memory_usage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    disk_usage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    network_usage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    latency: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    infrastructure: Mapped["Infrastructure"] = relationship(
        "Infrastructure",
        back_populates="metrics",
    )
