"""Custom exception hierarchy for AgentTwinOps.

All application-specific exceptions inherit from ``AppException``
so a single global handler can catch and serialise them uniformly.
"""

from __future__ import annotations

from typing import Any

from fastapi import status


class AppException(Exception):
    """Base exception for all application-level errors.

    Attributes
    ----------
    status_code:
        HTTP status code to return to the client.
    error_code:
        Machine-readable error code (e.g. ``"RESOURCE_NOT_FOUND"``).
    message:
        Human-readable explanation.
    details:
        Optional additional context for debugging.
    """

    def __init__(
        self,
        *,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        message: str = "An unexpected error occurred.",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundException(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        *,
        resource: str = "Resource",
        resource_id: str | None = None,
    ) -> None:
        detail_msg = f"{resource} not found"
        if resource_id:
            detail_msg += f" (id={resource_id})"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message=detail_msg,
        )


class ValidationException(AppException):
    """Raised when request data fails domain validation."""

    def __init__(
        self,
        *,
        message: str = "Validation failed.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class ConflictException(AppException):
    """Raised when an action conflicts with the current state."""

    def __init__(
        self,
        *,
        message: str = "Resource conflict.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message=message,
            details=details,
        )
