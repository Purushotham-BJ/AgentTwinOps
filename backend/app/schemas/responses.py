"""Shared Pydantic response schemas used across the API.

Keeping response shapes in one place ensures every endpoint returns
a consistent envelope.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Machine-readable error body."""

    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ApiResponse(BaseModel, Generic[T]):
    """Standard success envelope for all API responses."""

    success: bool = True
    data: T
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class ErrorResponse(BaseModel):
    """Standard error envelope for all API error responses."""

    success: bool = False
    error: ErrorDetail
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class HealthResponse(BaseModel):
    """Payload returned by the health-check endpoint."""

    status: str = "healthy"
    database: str = "unavailable"
    environment: str
    debug: bool
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class VersionResponse(BaseModel):
    """Payload returned by the version endpoint."""

    app_name: str
    version: str
    api_version: str = "v1"
    python_version: str


class RootResponse(BaseModel):
    """Payload returned by the root ``/`` endpoint."""

    app_name: str
    version: str
    docs_url: str
    health_url: str
    api_prefix: str
