"""Application factory — the single source of truth for creating the
FastAPI app instance.

This module follows the **Factory Pattern** so that tests, CLI scripts,
and the production ASGI server all create the app in exactly the same
way.  Middleware, exception handlers, and routers are wired here;
the factory itself stays thin by delegating to specialised modules.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.root import router as root_router
from app.api.v1.router import router as v1_router
from app.config.settings import Settings, get_settings
from app.core.lifespan import lifespan
from app.core.logging import setup_logging
from app.exceptions.handlers import register_exception_handlers


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and return a fully configured FastAPI application.

    Parameters
    ----------
    settings:
        Optional pre-built settings instance.  When ``None``,
        ``get_settings()`` is used (which reads from the environment).
        Passing an explicit value is useful in tests.

    Returns
    -------
    FastAPI
        The wired application, ready to be served by an ASGI server.
    """
    if settings is None:
        settings = get_settings()

    # ── 1. Logging (must be first) ──────────────────────────────
    setup_logging(settings)

    # ── 2. FastAPI instance ─────────────────────────────────────
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        debug=settings.APP_DEBUG,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {
                "name": "Root",
                "description": "API discovery and landing information.",
            },
            {
                "name": "System",
                "description": "Health checks, version info, and diagnostics.",
            },
        ],
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        contact={
            "name": "AgentTwinOps Team",
            "url": "https://github.com/RahulAnjanH/AgentTwinOps",
        },
    )

    # ── 3. CORS middleware ──────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # ── 4. Global exception handlers ───────────────────────────
    register_exception_handlers(app)

    # ── 5. Routers ──────────────────────────────────────────────
    app.include_router(root_router)
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)

    return app
