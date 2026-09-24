"""Incident API router."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.incident import Incident
from app.models.infrastructure import Infrastructure
from app.repositories.infrastructure import InfrastructureRepository
from app.schemas.incident import (
    IncidentCreateRequest,
    IncidentListResponse,
    IncidentResponse,
    IncidentUpdateRequest,
)
from app.schemas.responses import ApiResponse
from app.services.incident import IncidentService

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=ApiResponse[IncidentListResponse])
async def list_incidents(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    svc = IncidentService(session)
    items = await svc.list(offset=offset, limit=limit)
    resp_items = [
        IncidentResponse(
            id=i.id,
            service_id=i.service_id,
            severity=i.severity,
            incident_type=i.incident_type,
            resolution_status=i.resolution_status,
            timestamp=i.timestamp,
            created_at=i.created_at,
            updated_at=i.updated_at,
        )
        for i in items
    ]
    return ApiResponse(data=IncidentListResponse(items=resp_items, total=len(resp_items)))


@router.get("/{id}", response_model=ApiResponse[IncidentResponse])
async def get_incident(id: UUID, session: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    svc = IncidentService(session)
    incident = await svc.get(id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return ApiResponse(
        data=IncidentResponse(
            id=incident.id,
            service_id=incident.service_id,
            severity=incident.severity,
            incident_type=incident.incident_type,
            resolution_status=incident.resolution_status,
            timestamp=incident.timestamp,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
        )
    )


@router.post("", response_model=ApiResponse[IncidentResponse], status_code=status.HTTP_201_CREATED)
async def create_incident(
    payload: IncidentCreateRequest,
    session: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    infra_repo = InfrastructureRepository(session)
    infra = await infra_repo.get_by_id(payload.service_id)
    if not infra:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Referenced infrastructure not found")

    incident = Incident(
        service_id=payload.service_id,
        severity=payload.severity,
        incident_type=payload.incident_type,
        resolution_status=payload.resolution_status,
    )
    svc = IncidentService(session)
    try:
        created = await svc.create(incident)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Integrity error")
    return ApiResponse(
        data=IncidentResponse(
            id=created.id,
            service_id=created.service_id,
            severity=created.severity,
            incident_type=created.incident_type,
            resolution_status=created.resolution_status,
            timestamp=created.timestamp,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )
    )


@router.put("/{id}", response_model=ApiResponse[IncidentResponse])
async def update_incident(
    id: UUID,
    payload: IncidentUpdateRequest,
    session: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    svc = IncidentService(session)
    incident = await svc.get(id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    if payload.service_id is not None:
        infra_repo = InfrastructureRepository(session)
        infra = await infra_repo.get_by_id(payload.service_id)
        if not infra:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Referenced infrastructure not found")
        incident.service_id = payload.service_id
    if payload.severity is not None:
        incident.severity = payload.severity
    if payload.incident_type is not None:
        incident.incident_type = payload.incident_type
    if payload.resolution_status is not None:
        incident.resolution_status = payload.resolution_status

    try:
        updated = await svc.update(incident)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Integrity error")
    return ApiResponse(
        data=IncidentResponse(
            id=updated.id,
            service_id=updated.service_id,
            severity=updated.severity,
            incident_type=updated.incident_type,
            resolution_status=updated.resolution_status,
            timestamp=updated.timestamp,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )
    )
