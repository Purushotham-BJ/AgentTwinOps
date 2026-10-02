"""Authenticated prediction and simulation history APIs."""
from __future__ import annotations

from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.infrastructure import Infrastructure
from app.models.prediction import PredictionHistory
from app.models.simulation import SimulationHistory

router = APIRouter(tags=["History"])


@router.post("/predictions/history", status_code=status.HTTP_201_CREATED)
async def create_prediction_history(payload: dict, session: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    service_id = UUID(str(payload["service_id"]))
    if not await session.scalar(select(Infrastructure.id).where(Infrastructure.id == service_id)):
        raise HTTPException(status_code=404, detail="Infrastructure service not found")
    record = PredictionHistory(**{key: payload[key] for key in (
        "service_id", "prediction_type", "predicted_value", "confidence",
        "failure_probability", "risk_level", "factors", "recommended_action",
        "status", "horizon_minutes", "historical_metrics", "model_metrics",
        "prediction_source",
    )})
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return {"data": {"id": str(record.id), "created_at": record.created_at}}


@router.get("/predictions/history")
async def list_prediction_history(service_id: UUID | None = None, offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), session: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    query = select(PredictionHistory).order_by(PredictionHistory.created_at.desc()).offset(offset).limit(limit)
    if service_id:
        query = query.where(PredictionHistory.service_id == service_id)
    records = (await session.execute(query)).scalars().all()
    return {"items": [_prediction_dict(record) for record in records], "total": len(records)}


@router.post("/simulations/history", status_code=status.HTTP_201_CREATED)
async def create_simulation_history(payload: dict, session: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    service_id = UUID(str(payload["service_id"]))
    if not await session.scalar(select(Infrastructure.id).where(Infrastructure.id == service_id)):
        raise HTTPException(status_code=404, detail="Infrastructure service not found")
    values = {key: payload[key] for key in (
        "service_id", "scenario", "status", "baseline_state", "scenario_changes",
        "simulated_state", "simulated_health_score", "simulated_failure_probability",
        "simulated_operational_status", "impact_summary", "predicted_impact",
        "recommendations", "completed_at",
    )}
    if isinstance(values["completed_at"], str):
        values["completed_at"] = datetime.fromisoformat(values["completed_at"].replace("Z", "+00:00"))
    record = SimulationHistory(**values)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return {"data": {"id": str(record.id), "created_at": record.created_at}}


@router.get("/simulations/history")
async def list_simulation_history(service_id: UUID | None = None, offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), session: AsyncSession = Depends(get_db), _user=Depends(get_current_user)):
    query = select(SimulationHistory).order_by(SimulationHistory.created_at.desc()).offset(offset).limit(limit)
    if service_id:
        query = query.where(SimulationHistory.service_id == service_id)
    records = (await session.execute(query)).scalars().all()
    return {"items": [_simulation_dict(record) for record in records], "total": len(records)}


def _prediction_dict(record: PredictionHistory) -> dict:
    return {column.name: (str(value) if column.name in {"id", "service_id"} else value) for column in PredictionHistory.__table__.columns if (value := getattr(record, column.name)) is not None}


def _simulation_dict(record: SimulationHistory) -> dict:
    return {column.name: (str(value) if column.name in {"id", "service_id"} else value) for column in SimulationHistory.__table__.columns if (value := getattr(record, column.name)) is not None}
