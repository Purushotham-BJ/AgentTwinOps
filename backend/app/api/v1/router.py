from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.system import router as system_router
from app.api.v1.auth import router as auth_router
from app.api.v1.infrastructure import router as infrastructure_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.twins import router as twins_router

router = APIRouter()

# ── System (health, version) ───────────────────────────────────
router.include_router(system_router)
router.include_router(auth_router)
router.include_router(infrastructure_router)
router.include_router(incidents_router)
router.include_router(metrics_router)
router.include_router(twins_router)

# Future domain routers will be added below, e.g.:
# from app.api.v1.agents import router as agents_router
# router.include_router(agents_router, prefix="/agents", tags=["Agents"])
