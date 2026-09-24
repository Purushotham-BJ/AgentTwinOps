"""Infrastructure repository.

Supports basic CRUD and a few indexed filters (status, service_type).
Does not perform cascading deletes; relies on DB constraints.
"""
from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.infrastructure import Infrastructure, InfrastructureStatus
from app.repositories.base import BaseRepository


class InfrastructureRepository(BaseRepository[Infrastructure]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Infrastructure)

    async def get_by_id(self, id: UUID) -> Optional[Infrastructure]:
        return await super().get_by_id(id)

    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[Infrastructure]:
        return await super().list(offset=offset, limit=limit)

    async def create(self, infra: Infrastructure) -> Infrastructure:
        return await super().create(infra)

    async def update(self, infra: Infrastructure) -> Infrastructure:
        return await super().update(infra)

    async def delete(self, infra: Infrastructure) -> None:
        # Deleting an infrastructure that has incidents will raise an integrity
        # error due to ON DELETE RESTRICT; do not attempt cascade here.
        await super().delete(infra)

    async def list_by_status(
        self, status: InfrastructureStatus, offset: int = 0, limit: int = 100
    ) -> Sequence[Infrastructure]:
        stmt = select(Infrastructure).where(Infrastructure.status == status).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def list_by_type(self, service_type: str, offset: int = 0, limit: int = 100) -> Sequence[Infrastructure]:
        stmt = select(Infrastructure).where(Infrastructure.service_type == service_type).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()
