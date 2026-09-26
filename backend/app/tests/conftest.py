import sys
import asyncio
import os
import pytest
from alembic.config import Config
from alembic import command
from app.config.settings import get_settings

# On Windows, asyncpg works more reliably with the SelectorEventLoop.
if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

def _get_alembic_config():
    settings = get_settings()
    # Determine project root (backend directory)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
    alembic_ini_path = os.path.join(backend_dir, "alembic.ini")
    cfg = Config(alembic_ini_path)
    cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))
    return cfg

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Run Alembic migrations before any tests.

    This fixture runs synchronously before the test session starts.
    """
    cfg = _get_alembic_config()
    command.upgrade(cfg, "head")
    # No teardown needed; migrations remain for the session.
