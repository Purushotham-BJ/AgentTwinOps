"""Infrastructure service layer coordinating repository and business rules."""
from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.infrastructure import Infrastructure, InfrastructureStatus
from app.repositories.infrastructure import InfrastructureRepository


class InfrastructureService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = InfrastructureRepository(session)

    async def list(self, offset: int = 0, limit: int = 100, status: Optional[InfrastructureStatus] = None, service_type: Optional[str] = None) -> Sequence[Infrastructure]:
        if status is not None:
            return await self.repo.list_by_status(status, offset=offset, limit=limit)
        if service_type is not None:
            return await self.repo.list_by_type(service_type, offset=offset, limit=limit)
        return await self.repo.list(offset=offset, limit=limit)

    async def get(self, id: UUID) -> Optional[Infrastructure]:
        return await self.repo.get_by_id(id)

    async def create(self, infra: Infrastructure) -> Infrastructure:
        created = await self.repo.create(infra)
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        return created

    async def update(self, infra: Infrastructure) -> Infrastructure:
        updated = await self.repo.update(infra)
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        return updated

    async def delete(self, infra: Infrastructure) -> None:
        try:
            await self.repo.delete(infra)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        except Exception:
            await self.session.rollback()
            raise
