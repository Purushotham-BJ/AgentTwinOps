"""v1 system routes — health, version, and root information.

These endpoints carry no business logic and are always available,
even when downstream services (DB, Redis, etc.) are not yet wired.
"""

from __future__ import annotations

import platform

from fastapi import APIRouter, Depends

from app.config.settings import Settings, get_settings
from app.schemas.responses import (
    ApiResponse,
    HealthResponse,
    RootResponse,
    VersionResponse,
)

router = APIRouter(tags=["System"])

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, check_database


@router.get(
    "/health",
    response_model=ApiResponse[HealthResponse],
    summary="Health check",
    description="Returns the current health status of the API and its dependencies.",
)
async def health_check(
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[HealthResponse]:
    """Lightweight liveness / readiness probe."""
    db_status = await check_database(db)
    
    # If the DB is unavailable, the overall API might still be running, 
    # but we might want to mark the API status differently. For now, 
    # we return 'healthy' for the API if it can respond, but database 
    # status will indicate if the DB is reachable.
    
    return ApiResponse(
        data=HealthResponse(
            status="healthy" if db_status == "connected" else "degraded",
            database=db_status,
            environment=settings.APP_ENV,
            debug=settings.APP_DEBUG,
        ),
    )


@router.get(
    "/version",
    response_model=ApiResponse[VersionResponse],
    summary="API version",
    description="Returns version information for the running API instance.",
)
async def version(
    settings: Settings = Depends(get_settings),
) -> ApiResponse[VersionResponse]:
    """Expose build / runtime version metadata."""
    return ApiResponse(
        data=VersionResponse(
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
            api_version="v1",
            python_version=platform.python_version(),
        ),
    )
