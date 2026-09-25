from typing import Sequence
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.metric import Metric
from app.schemas.metric import MetricCreate
from app.services.twin_service import TwinService


class MetricService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.twin_service = TwinService(session)

    async def get_metric(self, metric_id: UUID) -> Metric | None:
        stmt = select(Metric).where(Metric.id == metric_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_metrics(self, skip: int = 0, limit: int = 100) -> Sequence[Metric]:
        stmt = select(Metric).order_by(desc(Metric.timestamp)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_metrics_by_service(
        self,
        service_id: UUID,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 100,
        skip: int = 0,
    ) -> Sequence[Metric]:
        stmt = select(Metric).where(Metric.service_id == service_id)
        if start:
            stmt = stmt.where(Metric.timestamp >= start)
        if end:
            stmt = stmt.where(Metric.timestamp <= end)
        stmt = stmt.order_by(desc(Metric.timestamp)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_latest_metric(self, service_id: UUID) -> Metric | None:
        stmt = (
            select(Metric)
            .where(Metric.service_id == service_id)
            .order_by(desc(Metric.timestamp))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def ingest_metric(self, metric_in: MetricCreate) -> Metric:
        metric = Metric(
            service_id=metric_in.service_id,
            cpu_usage=metric_in.cpu_usage,
            memory_usage=metric_in.memory_usage,
            disk_usage=metric_in.disk_usage,
            network_usage=metric_in.network_usage,
            latency=metric_in.latency,
        )
        self.session.add(metric)
        await self.session.flush()
        # Synchronize twin after metric persisted
        await self.twin_service.synchronize_twin(metric_in.service_id, metric)
        await self.session.commit()
        await self.session.refresh(metric)
        return metric
