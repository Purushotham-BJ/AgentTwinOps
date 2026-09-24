import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from app.config.settings import get_settings
from app.database import engine, get_db, check_database


@pytest.mark.asyncio
async def test_database_configuration_loads():
    """Test 1: Database configuration loads successfully."""
    settings = get_settings()
    assert settings.DATABASE_URL.startswith("postgresql+asyncpg://")


@pytest.mark.asyncio
async def test_sqlalchemy_engine_initializes():
    """Test 2: SQLAlchemy engine initializes."""
    assert isinstance(engine, AsyncEngine)
    assert engine.url.drivername == "postgresql+asyncpg"


@pytest.mark.asyncio
async def test_async_session_factory_initializes():
    """Test 3: Async session factory initializes."""
    from app.database.session import async_session_factory
    assert async_session_factory.class_ == AsyncSession
    assert async_session_factory.kw["expire_on_commit"] is False


@pytest.mark.asyncio
async def test_fastapi_database_dependency():
    """Test 4: FastAPI database dependency can create a session."""
    db_gen = get_db()
    # It's an async generator, so we can get the next item
    session = await anext(db_gen)
    assert isinstance(session, AsyncSession)
    assert session.is_active
    
    # Close it properly
    await session.close()


@pytest.mark.asyncio
async def test_postgresql_connectivity_works():
    """Test 5: PostgreSQL connectivity works."""
    # We will use check_database to run SELECT 1
    db_gen = get_db()
    session = await anext(db_gen)
    
    try:
        status = await check_database(session)
        # We handle this gracefully if postgres is not running locally.
        # But if it is running, it should return 'connected'.
        # For the sake of the test, we just ensure it doesn't crash and returns one of the statuses.
        assert status in ["connected", "unavailable"]
        
        if status == "unavailable":
            pytest.skip("PostgreSQL is unavailable. Please start it at localhost:5432 to test connectivity fully.")
    finally:
        await session.close()
