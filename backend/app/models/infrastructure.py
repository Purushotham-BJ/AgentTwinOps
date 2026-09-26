"""Infrastructure ORM model for AgentTwinOps."""

from datetime import datetime, timezone
import enum
from typing import TYPE_CHECKING, List
import uuid

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.incident import Incident
    from app.models.metric import Metric
    from app.models.twin import Twin, TwinHistory


class InfrastructureStatus(str, enum.Enum):
    """Infrastructure operational status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class Infrastructure(Base):
    """Infrastructure model representing monitored cloud resources and services.

    Maps to the operational infrastructure table in PostgreSQL.
    """

    __tablename__ = "infrastructure"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    service_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    service_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    status: Mapped[InfrastructureStatus] = mapped_column(
        Enum(
            InfrastructureStatus,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=InfrastructureStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    host: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
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
    incidents: Mapped[List["Incident"]] = relationship(
        "Incident",
        back_populates="infrastructure",
        lazy="selectin",
    )
    metrics: Mapped[List["Metric"]] = relationship(
        "Metric",
        back_populates="infrastructure",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    twin: Mapped["Twin"] = relationship(
        "Twin",
        back_populates="infrastructure",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )

    @property
    def service_id(self) -> uuid.UUID:
        """Alias for id to match documentation field naming."""
        return self.id

    def __repr__(self) -> str:
        return (
            f"<Infrastructure(id={self.id}, service_name='{self.service_name}', "
            f"service_type='{self.service_type}', status='{self.status}')>"
        )
