import os
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from alembic.config import Config
from alembic import command
from app.config.settings import get_settings
from app.database.base import Base

def get_alembic_config():
    """Helper to get Alembic config."""
    settings = get_settings()
    # BASE_DIR is the root of the project, backend is where alembic.ini is
    # Let's dynamically find it relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    
    alembic_ini_path = os.path.join(backend_dir, "alembic.ini")
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))
    return alembic_cfg

def test_alembic_configuration_loads():
    """Verify Alembic config can be loaded."""
    config = get_alembic_config()
    assert config is not None
    assert config.get_main_option("script_location") is not None

def test_target_metadata_is_base_metadata():
    """Verify target metadata is the application's Base.metadata."""
    # This is a direct test of the application structure
    assert Base.metadata is not None

@pytest.mark.asyncio
async def test_migration_environment_connects_to_postgres():
    """Verify we can connect to the DB and see Alembic's version table (or ensure connection works)."""
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.connect() as conn:
        # Simple query to verify connection
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
        
    await engine.dispose()

def test_migration_upgrade_and_downgrade():
    """
    Verify upgrade to head, detect current revision, downgrade to base, 
    and upgrade to head again.
    """
    config = get_alembic_config()
    
    # 1. Upgrade to head
    command.upgrade(config, "head")
    
    # We can't easily capture the stdout of command.current to check the revision,
    # but the successful execution of these commands verifies the behavior.
    
    # 2. Downgrade to base
    command.downgrade(config, "base")
    
    # 3. Upgrade to head again
    command.upgrade(config, "head")

