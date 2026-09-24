"""Incident service layer coordinating repository and business rules."""
from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident, IncidentSeverity, ResolutionStatus
from app.repositories.incident import IncidentRepository


class IncidentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = IncidentRepository(session)

    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[Incident]:
        return await self.repo.list(offset=offset, limit=limit)

    async def get(self, id: UUID) -> Optional[Incident]:
        return await self.repo.get_by_id(id)

    async def create(self, incident: Incident) -> Incident:
        created = await self.repo.create(incident)
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        return created

    async def update(self, incident: Incident) -> Incident:
        updated = await self.repo.update(incident)
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        return updated
