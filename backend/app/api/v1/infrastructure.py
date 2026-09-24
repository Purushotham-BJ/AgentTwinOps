"""Infrastructure API router: CRUD and list endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.schemas.responses import ApiResponse
from app.schemas.infrastructure import (
    InfrastructureCreateRequest,
    InfrastructureUpdateRequest,
    InfrastructureResponse,
    InfrastructureListResponse,
)
from app.dependencies.auth import get_current_user
from app.database.session import get_db
from app.services.infrastructure import InfrastructureService
from app.models.infrastructure import Infrastructure, InfrastructureStatus

router = APIRouter(prefix="/infrastructure", tags=["Infrastructure"])


@router.get("", response_model=ApiResponse[InfrastructureListResponse])
async def list_infrastructure(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    svc = InfrastructureService(session)
    items = await svc.list(offset=offset, limit=limit)
    resp_items = [InfrastructureResponse(
        id=i.id,
        service_name=i.service_name,
        service_type=i.service_type,
        status=i.status,
        host=i.host,
        created_at=i.created_at,
        updated_at=i.updated_at,
    ) for i in items]
    return ApiResponse(data=InfrastructureListResponse(items=resp_items, total=len(resp_items)))


@router.get("/{id}", response_model=ApiResponse[InfrastructureResponse])
async def get_infrastructure(id: UUID, session: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    svc = InfrastructureService(session)
    infra = await svc.get(id)
    if not infra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Infrastructure not found")
    return ApiResponse(data=InfrastructureResponse(
        id=infra.id,
        service_name=infra.service_name,
        service_type=infra.service_type,
        status=infra.status,
        host=infra.host,
        created_at=infra.created_at,
        updated_at=infra.updated_at,
    ))


@router.post("", response_model=ApiResponse[InfrastructureResponse], status_code=status.HTTP_201_CREATED)
async def create_infrastructure(payload: InfrastructureCreateRequest, session: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    svc = InfrastructureService(session)
    infra = Infrastructure(
        service_name=payload.service_name,
        service_type=payload.service_type,
        status=payload.status or InfrastructureStatus.ACTIVE,
        host=payload.host,
    )
    try:
        created = await svc.create(infra)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Integrity error")
    return ApiResponse(data=InfrastructureResponse(
        id=created.id,
        service_name=created.service_name,
        service_type=created.service_type,
        status=created.status,
        host=created.host,
        created_at=created.created_at,
        updated_at=created.updated_at,
    ))


@router.put("/{id}", response_model=ApiResponse[InfrastructureResponse])
async def update_infrastructure(id: UUID, payload: InfrastructureUpdateRequest, session: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    svc = InfrastructureService(session)
    infra = await svc.get(id)
    if not infra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Infrastructure not found")
    # Apply allowed updates only
    if payload.service_name is not None:
        infra.service_name = payload.service_name
    if payload.service_type is not None:
        infra.service_type = payload.service_type
    if payload.status is not None:
        infra.status = payload.status
    if payload.host is not None:
        infra.host = payload.host
    try:
        updated = await svc.update(infra)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Integrity error")
    return ApiResponse(data=InfrastructureResponse(
        id=updated.id,
        service_name=updated.service_name,
        service_type=updated.service_type,
        status=updated.status,
        host=updated.host,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    ))


@router.delete("/{id}", response_model=ApiResponse[dict])
async def delete_infrastructure(id: UUID, session: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    svc = InfrastructureService(session)
    infra = await svc.get(id)
    if not infra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Infrastructure not found")
    try:
        await svc.delete(infra)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Infrastructure is referenced by incidents and cannot be deleted")
    return ApiResponse(data={"message": "Deleted"})
