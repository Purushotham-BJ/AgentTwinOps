"""Database session factory and dependency."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.engine import engine

# Create the session factory
# expire_on_commit=False is important for async to avoid implicit blocking lazy loads
# outside of the transaction scope.
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing a database session to FastAPI routes.
    
    Yields an AsyncSession, ensuring it is closed after the request completes.
    """
    async with async_session_factory() as session:
        yield session
