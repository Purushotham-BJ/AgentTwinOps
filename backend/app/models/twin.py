"""Twin ORM models for AgentTwinOps."""

from datetime import datetime, timezone
import uuid
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List, Dict, Any

from sqlalchemy import DateTime, Float, ForeignKey, func, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.infrastructure import Infrastructure


class TwinOperationalStatus(str, PyEnum):
    """Operational status classification for a twin."""
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"
    STALE = "STALE"


class Twin(Base):
    """Digital Twin model representing current state.

    Maps to the twins table in PostgreSQL.
    """

    __tablename__ = "twins"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("infrastructure.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Core state fields
    current_state: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default='{}')
    predicted_state: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default='{}')
    health_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    failure_probability: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Sprint 5 extensions
    operational_status: Mapped[str] = mapped_column(
        Enum(TwinOperationalStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        default=TwinOperationalStatus.UNKNOWN,
        nullable=False,
        index=True,
    )
    state_version: Mapped[int] = mapped_column(default=0, nullable=False)
    trends: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default='{}')
    anomalies: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, nullable=False, server_default='[]')

    last_sync: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    infrastructure: Mapped["Infrastructure"] = relationship(
        "Infrastructure",
        back_populates="twin",
    )
    history: Mapped[List["TwinHistory"]] = relationship(
        "TwinHistory",
        back_populates="twin",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class TwinHistory(Base):
    """Twin history model representing past states.

    Maps to the twin_history table in PostgreSQL.
    """

    __tablename__ = "twin_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    twin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("twins.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Sprint 5 extension – version of the twin this snapshot belongs to
    state_version: Mapped[int] = mapped_column(default=0, nullable=False)

    state: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default='{}')
    health_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    twin: Mapped["Twin"] = relationship(
        "Twin",
        back_populates="history",
    )
