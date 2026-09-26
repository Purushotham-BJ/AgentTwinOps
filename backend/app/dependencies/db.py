'''Database dependency for FastAPI routes.
Provides an async SQLAlchemy session via dependency injection.
'''

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session and ensure it is closed after use.
    This mirrors the typical FastAPI dependency pattern for DB sessions.
    """
    async with async_session_factory() as session:
        yield session
