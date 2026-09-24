"""Pydantic schemas for Incident APIs."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.incident import IncidentSeverity, ResolutionStatus


class IncidentCreateRequest(BaseModel):
    service_id: UUID
    severity: Optional[IncidentSeverity] = IncidentSeverity.MEDIUM
    incident_type: str = Field(..., min_length=1, max_length=100)
    resolution_status: Optional[ResolutionStatus] = ResolutionStatus.OPEN


class IncidentUpdateRequest(BaseModel):
    service_id: Optional[UUID] = None
    severity: Optional[IncidentSeverity] = None
    incident_type: Optional[str] = Field(default=None, min_length=1, max_length=100)
    resolution_status: Optional[ResolutionStatus] = None


class IncidentResponse(BaseModel):
    id: UUID
    service_id: UUID
    severity: IncidentSeverity
    incident_type: str
    resolution_status: ResolutionStatus
    timestamp: datetime
    created_at: datetime
    updated_at: datetime


class IncidentListResponse(BaseModel):
    items: list[IncidentResponse]
    total: int
