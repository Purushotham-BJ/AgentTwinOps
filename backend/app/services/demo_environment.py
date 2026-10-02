"""Idempotent shared onboarding demo environment initialization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.demo_environment import DemoEnvironment
from app.models.incident import Incident, IncidentSeverity, ResolutionStatus
from app.models.infrastructure import Infrastructure, InfrastructureStatus
from app.models.metric import Metric
from app.services.twin_service import TwinService

logger = logging.getLogger(__name__)

DEMO_SEED_KEY = "agenttwinops-default-demo"
DEMO_VERSION = "v1"
METRIC_COUNT = 30


@dataclass(frozen=True)
class DemoServiceSpec:
    name: str
    service_type: str
    host: str


DEMO_SERVICES = (
    DemoServiceSpec("demo-api-gateway", "api_gateway", "demo-api-gateway"),
    DemoServiceSpec("demo-user-service", "microservice", "demo-user-service"),
    DemoServiceSpec("demo-payment-service", "microservice", "demo-payment-service"),
    DemoServiceSpec("demo-order-service", "microservice", "demo-order-service"),
    DemoServiceSpec("demo-database-service", "database", "demo-database-service"),
)


async def initialize_default_demo_environment(
    session: AsyncSession,
    initialized_by_user_id: UUID | None = None,
) -> bool:
    """Create the shared demo environment once.

    Operational data is intentionally global in the current architecture.
    The registry prevents one copy per user while retaining an audit link to
    the first account that triggered initialization.
    """
    existing = await session.scalar(
        select(DemoEnvironment).where(DemoEnvironment.seed_key == DEMO_SEED_KEY)
    )
    if existing and existing.status == "ready":
        return False

    if not existing:
        existing = DemoEnvironment(
            seed_key=DEMO_SEED_KEY,
            version=DEMO_VERSION,
            status="initializing",
            initialized_by_user_id=initialized_by_user_id,
        )
        session.add(existing)
        try:
            await session.flush()
        except IntegrityError:
            await session.rollback()
            existing = await session.scalar(
                select(DemoEnvironment).where(DemoEnvironment.seed_key == DEMO_SEED_KEY)
            )
            if existing and existing.status == "ready":
                return False
            raise

    try:
        services = await _ensure_services(session)
        await _ensure_metrics_and_twins(session, services, existing.created_at)
        await _ensure_incidents(session, services)
        existing.status = "ready"
        existing.version = DEMO_VERSION
        await session.commit()
        logger.info("Default demo environment initialized (%s services)", len(services))
        return True
    except Exception:
        await session.rollback()
        if existing:
            existing.status = "failed"
            session.add(existing)
            await session.commit()
        raise


async def _ensure_services(session: AsyncSession) -> dict[str, Infrastructure]:
    services: dict[str, Infrastructure] = {}
    for spec in DEMO_SERVICES:
        service = await session.scalar(
            select(Infrastructure).where(Infrastructure.service_name == spec.name)
        )
        if service and (service.service_type != spec.service_type or service.host != spec.host):
            raise RuntimeError(
                f"Reserved demo service name is already used by incompatible infrastructure: {spec.name}"
            )
        if not service:
            service = Infrastructure(
                service_name=spec.name,
                service_type=spec.service_type,
                status=InfrastructureStatus.ACTIVE,
                host=spec.host,
            )
            session.add(service)
            await session.flush()
        services[spec.name] = service
    return services


def _metric_values(service_name: str, index: int) -> tuple[float, float, float, float, float]:
    if service_name.endswith("payment-service"):
        return 58 + index * 0.6, 61 + index * 0.55, 42, 1000 + index * 35, 180 + index * 14
    if service_name.endswith("database-service"):
        return 42 + index * 0.15, 64 + index * 0.3, 72 + index * 0.15, 2200 + index * 40, 360 + index * 6
    if service_name.endswith("order-service"):
        spike = 18 if index in (12, 24) else 0
        return 35 + spike + index * 0.12, 48 + index * 0.1, 38, 1400 + index * 25, 100 + spike * 4
    if service_name.endswith("user-service"):
        return 38 + index * 0.08, 52 + index * 0.1, 34, 900 + index * 18, 95
    return 32 + index * 0.1, 46 + index * 0.1, 30, 1200 + index * 22, 80


async def _ensure_metrics_and_twins(
    session: AsyncSession,
    services: dict[str, Infrastructure],
    created_at: datetime,
) -> None:
    twin_service = TwinService(session)
    for service_name, service in services.items():
        for index in range(METRIC_COUNT):
            timestamp = created_at + timedelta(minutes=index * 10)
            existing = await session.scalar(
                select(Metric).where(
                    Metric.service_id == service.id,
                    Metric.timestamp == timestamp,
                )
            )
            if existing:
                continue
            cpu, memory, disk, network, latency = _metric_values(service_name, index)
            metric = Metric(
                service_id=service.id,
                cpu_usage=min(cpu, 99.0),
                memory_usage=min(memory, 99.0),
                disk_usage=min(disk, 99.0),
                network_usage=network,
                latency=latency,
                timestamp=timestamp,
            )
            session.add(metric)
            await session.flush()
            await twin_service.synchronize_twin(service.id, metric)


async def _ensure_incidents(
    session: AsyncSession,
    services: dict[str, Infrastructure],
) -> None:
    incidents = (
        (services["demo-payment-service"], IncidentSeverity.HIGH, "demo-v1-high-latency", ResolutionStatus.OPEN),
        (services["demo-database-service"], IncidentSeverity.MEDIUM, "demo-v1-memory-warning", ResolutionStatus.RESOLVED),
        (services["demo-api-gateway"], IncidentSeverity.LOW, "demo-v1-temporary-latency", ResolutionStatus.RESOLVED),
    )
    for service, severity, incident_type, resolution_status in incidents:
        exists = await session.scalar(
            select(Incident).where(
                Incident.service_id == service.id,
                Incident.incident_type == incident_type,
            )
        )
        if not exists:
            session.add(
                Incident(
                    service_id=service.id,
                    severity=severity,
                    incident_type=incident_type,
                    resolution_status=resolution_status,
                )
            )
