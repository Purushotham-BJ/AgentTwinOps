"""SQLAlchemy asynchronous engine configuration."""

import logging
from sqlalchemy.ext.asyncio import create_async_engine

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()

# We set pool_pre_ping to True to ensure connections are alive before use
# echo is based on APP_DEBUG to log SQL statements during development
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
