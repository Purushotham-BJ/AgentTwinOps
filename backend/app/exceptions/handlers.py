"""Global exception handlers registered on the FastAPI application.

These handlers ensure that *every* error — including unhandled ones —
returns a consistent JSON envelope instead of the framework default
HTML or plaintext tracebacks.
"""

from __future__ import annotations

import logging
import traceback

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.base import AppException

logger = logging.getLogger(__name__)


def _safe_validation_errors(exc: RequestValidationError) -> list[dict]:
    """Make validation details serializable without exposing password input."""
    safe_errors = []
    for error in exc.errors():
        safe_error = dict(error)
        if safe_error.get("loc") and "password" in safe_error["loc"]:
            safe_error.pop("input", None)
        context = safe_error.get("ctx")
        if context and "error" in context:
            safe_error["ctx"] = {**context, "error": str(context["error"])}
        safe_errors.append(safe_error)
    return safe_errors


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to *app*.

    Parameters
    ----------
    app:
        The FastAPI instance produced by the application factory.
    """

    @app.exception_handler(AppException)
    async def _app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        """Handle known application exceptions."""
        logger.warning(
            "AppException: code=%s message=%s path=%s",
            exc.error_code,
            exc.message,
            request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle Pydantic / path-param validation failures."""
        safe_errors = _safe_validation_errors(exc)
        logger.warning(
            "RequestValidationError: path=%s errors=%s",
            request.url.path,
            safe_errors,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed.",
                    "details": safe_errors,
                },
            },
        )

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Catch-all for truly unexpected errors."""
        logger.error(
            "Unhandled exception: path=%s\n%s",
            request.url.path,
            traceback.format_exc(),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected internal error occurred.",
                    "details": {},
                },
            },
        )
