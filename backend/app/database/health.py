"""Database connectivity health check."""

import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def check_database(session: AsyncSession) -> str:
    """Check database connectivity by executing a simple SELECT 1.
    
    Returns 'connected' if successful, 'unavailable' otherwise.
    Never exposes internal database errors.
    """
    try:
        await session.execute(text("SELECT 1"))
        return "connected"
    except Exception as e:
        # Log the specific error for internal debugging
        logger.error("Database health check failed: %s", str(e), exc_info=True)
        # Return generic status to the caller
        return "unavailable"
