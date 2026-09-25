from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from typing import Any, Dict, List
from uuid import UUID

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.twin import Twin, TwinHistory
from app.schemas.twin import TwinResponse, TwinHistoryResponse
from app.services.twin_service import TwinService

router = APIRouter(prefix="/twins", tags=["twins"])


# ---------------------------------------------------------------------------
# GET /twins/by-service/{service_id}
# Must be declared BEFORE /{twin_id} so FastAPI does not misinterpret the
# literal "by-service" as a UUID path parameter.
# ---------------------------------------------------------------------------

@router.get("/by-service/{service_id}", response_model=TwinResponse)
async def get_twin_by_service(
    service_id: UUID,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Return the digital twin for a given infrastructure service."""
    svc = TwinService(db)
    twin = await svc.get_twin_by_service_id(service_id)
    if not twin:
        raise HTTPException(status_code=404, detail="Twin not found for service")
    return twin


# ---------------------------------------------------------------------------
# PATCH /twins/by-service/{service_id}/predicted-state
# Called by the AI service to persist a new predicted_state after a
# successful ML prediction.  current_state is never touched here.
# ---------------------------------------------------------------------------


class PredictedStatePayload(BaseModel):
    predicted_state: Dict[str, Any]


@router.patch(
    "/by-service/{service_id}/predicted-state",
    response_model=TwinResponse,
    status_code=status.HTTP_200_OK,
)
async def update_predicted_state(
    service_id: UUID,
    payload: PredictedStatePayload,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Update only the predicted_state of a twin.

    Does NOT modify current_state, health_score, operational_status,
    trends, anomalies, or state_version.
    """
    svc = TwinService(db)
    try:
        twin = await svc.update_predicted_state(service_id, payload.predicted_state)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update predicted state: {exc}",
        )
    return twin


# ---------------------------------------------------------------------------
# GET /twins/{twin_id}
# ---------------------------------------------------------------------------

@router.get("/{twin_id}", response_model=TwinResponse)
async def get_twin(
    twin_id: UUID,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Return a twin by its own UUID."""
    result = await db.execute(select(Twin).where(Twin.id == twin_id))
    twin = result.scalars().first()
    if not twin:
        raise HTTPException(status_code=404, detail="Twin not found")
    return twin


# ---------------------------------------------------------------------------
# GET /twins/{twin_id}/history
# ---------------------------------------------------------------------------

@router.get("/{twin_id}/history", response_model=List[TwinHistoryResponse])
async def get_twin_history(
    twin_id: UUID,
    limit: int = 100,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Return the state history for a twin."""
    stmt = (
        select(TwinHistory)
        .where(TwinHistory.twin_id == twin_id)
        .order_by(TwinHistory.timestamp.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# GET /twins/
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[TwinResponse])
async def list_twins(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Return all digital twins."""
    result = await db.execute(select(Twin))
    return result.scalars().all()
