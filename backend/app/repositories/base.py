"""Base repository utilities for AgentTwinOps.

Provides a small, minimal generic repository abstraction that concrete
repositories can extend. It intentionally does not manage transactions
or commits — that responsibility remains with higher layers.
"""
from __future__ import annotations

from typing import Generic, Optional, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Minimal generic repository.

    - Keeps a reference to an injected AsyncSession
    - Provides small helpers (get_by_id, list, create, update, delete)
    - Does not call `commit()`; callers control transactions.
    """

    def __init__(self, session: AsyncSession, model: Type[ModelType]) -> None:
        self.session = session
        self.model = model

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        # The object is expected to be attached to the session. Flush to persist.
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        await self.session.delete(obj)
        await self.session.flush()
