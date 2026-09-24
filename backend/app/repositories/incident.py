"""Incident repository.

Provides CRUD and common incident filters used by the service layer.
"""
from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import desc, not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident, IncidentSeverity, ResolutionStatus
from app.repositories.base import BaseRepository


class IncidentRepository(BaseRepository[Incident]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Incident)

    async def get_by_id(self, id: UUID) -> Optional[Incident]:
        return await super().get_by_id(id)

    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[Incident]:
        return await super().list(offset=offset, limit=limit)

    async def create(self, incident: Incident) -> Incident:
        return await super().create(incident)

    async def update(self, incident: Incident) -> Incident:
        return await super().update(incident)

    async def delete(self, incident: Incident) -> None:
        await super().delete(incident)

    async def list_by_service(self, service_id: UUID, offset: int = 0, limit: int = 100) -> Sequence[Incident]:
        stmt = select(Incident).where(Incident.service_id == service_id).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def list_by_severity(self, severity: IncidentSeverity, offset: int = 0, limit: int = 100) -> Sequence[Incident]:
        stmt = select(Incident).where(Incident.severity == severity).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def list_by_resolution_status(
        self, status: ResolutionStatus, offset: int = 0, limit: int = 100
    ) -> Sequence[Incident]:
        stmt = select(Incident).where(Incident.resolution_status == status).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def list_unresolved(self, offset: int = 0, limit: int = 100) -> Sequence[Incident]:
        stmt = select(Incident).where(
            not_(Incident.resolution_status.in_([ResolutionStatus.RESOLVED, ResolutionStatus.CLOSED]))
        ).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def list_recent(self, limit: int = 50) -> Sequence[Incident]:
        stmt = select(Incident).order_by(desc(Incident.timestamp)).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()
