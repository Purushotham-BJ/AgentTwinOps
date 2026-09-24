"""Application lifespan management.

Uses the modern ``asynccontextmanager`` pattern introduced in
FastAPI ≥ 0.93 (replacing the deprecated ``@app.on_event`` callbacks).

Startup and shutdown logic is centralised here so the application
factory stays thin and testable.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.settings import get_settings
from app.database.engine import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown lifecycle.

    Parameters
    ----------
    app:
        The FastAPI application instance.

    Yields
    ------
    None
        Control returns to the ASGI server while the app is running.
    """
    settings = get_settings()

    # ── STARTUP ─────────────────────────────────────────────────
    logger.info(
        "[STARTUP] %s v%s starting -- env=%s debug=%s",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.APP_ENV,
        settings.APP_DEBUG,
    )

    # Future startup tasks (DB pool, Redis connection, etc.)
    # will be added here as the application grows.

    yield  # ← Application runs while suspended here

    # ── SHUTDOWN ────────────────────────────────────────────────
    logger.info(
        "[SHUTDOWN] %s shutting down -- cleaning up resources ...",
        settings.APP_NAME,
    )

    # Clean up DB engine/pool to ensure connections are closed before
    # the event loop is torn down (prevents asyncpg "Event loop is closed" errors).
    try:
        logger.info("[SHUTDOWN] Disposing database engine/pool ...")
        await engine.dispose()
        logger.info("[SHUTDOWN] Database engine disposed.")
    except Exception:
        logger.exception("Error while disposing database engine during shutdown")

    logger.info("[SHUTDOWN] Shutdown complete.")
