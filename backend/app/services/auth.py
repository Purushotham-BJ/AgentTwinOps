"""Authentication service coordinating UserRepository, hashing and tokens."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.security.password_policy import validate_password_strength


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, name: str, email: str, password: str) -> User:
        # normalize email
        email = email.strip().lower()
        validate_password_strength(password)
        hashed = hash_password(password)
        user = User(name=name, email=email, password=hashed)
        try:
            created = await self.user_repo.create(user)
            await self.session.commit()
            return created
        except IntegrityError:
            await self.session.rollback()
            raise

    async def authenticate(self, email: str, password: str) -> Optional[str]:
        email = email.strip().lower()
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        if not user.password or not verify_password(password, user.password):
            return None
        token = create_access_token(user.id)
        return token
