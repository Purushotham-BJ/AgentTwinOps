"""User repository implementation.

Contains operations for persisting and retrieving `User` model objects.
This module intentionally contains no business logic or authentication code.
"""
from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_id(self, id: UUID) -> Optional[User]:
        return await super().get_by_id(id)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[User]:
        return await super().list(offset=offset, limit=limit)

    async def create(self, user: User) -> User:
        # Password must already be hashed by caller.
        return await super().create(user)

    async def update(self, user: User) -> User:
        return await super().update(user)

    async def delete(self, user: User) -> None:
        await super().delete(user)
