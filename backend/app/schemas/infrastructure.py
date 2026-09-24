"""Pydantic schemas for Infrastructure APIs."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

from app.models.infrastructure import InfrastructureStatus


class InfrastructureCreateRequest(BaseModel):
    service_name: str = Field(..., min_length=1)
    service_type: str = Field(..., min_length=1)
    status: Optional[InfrastructureStatus] = None
    host: str = Field(..., min_length=1)


class InfrastructureUpdateRequest(BaseModel):
    service_name: Optional[str] = None
    service_type: Optional[str] = None
    status: Optional[InfrastructureStatus] = None
    host: Optional[str] = None


class InfrastructureResponse(BaseModel):
    id: UUID
    service_name: str
    service_type: str
    status: InfrastructureStatus
    host: str
    created_at: datetime
    updated_at: datetime


class InfrastructureListResponse(BaseModel):
    items: list[InfrastructureResponse]
    total: int
