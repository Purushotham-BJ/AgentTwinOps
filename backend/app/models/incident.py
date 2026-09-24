"""Incident ORM model for AgentTwinOps."""

from datetime import datetime, timezone
import enum
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.infrastructure import Infrastructure


class IncidentSeverity(str, enum.Enum):
    """Incident severity enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResolutionStatus(str, enum.Enum):
    """Incident resolution status enumeration."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Incident(Base):
    """Incident model representing infrastructure incidents and anomalies.

    Maps to the operational incident table in PostgreSQL.
    Supports querying by service, severity, resolution status, and timestamp.
    """

    __tablename__ = "incidents"
    __table_args__ = (
        Index("ix_incidents_service_status", "service_id", "resolution_status"),
        Index("ix_incidents_status_severity", "resolution_status", "severity"),
        Index("ix_incidents_service_timestamp", "service_id", "timestamp"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("infrastructure.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(
            IncidentSeverity,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=IncidentSeverity.MEDIUM,
        nullable=False,
        index=True,
    )
    incident_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    resolution_status: Mapped[ResolutionStatus] = mapped_column(
        Enum(
            ResolutionStatus,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=ResolutionStatus.OPEN,
        nullable=False,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    infrastructure: Mapped["Infrastructure"] = relationship(
        "Infrastructure",
        back_populates="incidents",
    )

    @property
    def incident_id(self) -> uuid.UUID:
        """Alias for id to match documentation field naming."""
        return self.id

    def __repr__(self) -> str:
        return (
            f"<Incident(id={self.id}, service_id={self.service_id}, "
            f"severity='{self.severity}', type='{self.incident_type}', status='{self.resolution_status}')>"
        )
