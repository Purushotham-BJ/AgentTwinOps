"""Root-level router — mounted directly on ``/``.

Contains the landing endpoint that describes the API to first-time
visitors and automated discovery tools.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config.settings import Settings, get_settings
from app.schemas.responses import ApiResponse, RootResponse

router = APIRouter(tags=["Root"])


@router.get(
    "/",
    response_model=ApiResponse[RootResponse],
    summary="API root",
    description="Landing page with discovery links for the AgentTwinOps API.",
)
async def root(
    settings: Settings = Depends(get_settings),
) -> ApiResponse[RootResponse]:
    """Return entry-point metadata for the API."""
    return ApiResponse(
        data=RootResponse(
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
            docs_url="/docs",
            health_url=f"{settings.API_V1_PREFIX}/health",
            api_prefix=settings.API_V1_PREFIX,
        ),
    )
