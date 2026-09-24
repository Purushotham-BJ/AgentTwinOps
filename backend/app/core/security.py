"""Security utilities: password hashing and JWT token handling."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from argon2 import PasswordHasher
from jose import JWTError, jwt

from app.config.settings import get_settings

settings = get_settings()

# Argon2 password hasher instance
_ph = PasswordHasher()


def hash_password(password: str) -> str:
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters")
    return _ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _ph.verify(hashed_password, plain_password)
    except Exception:
        return False


def create_access_token(subject: UUID, expires_delta: int | None = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=(expires_delta or settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY.get_secret_value(), algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as exc:
        raise
