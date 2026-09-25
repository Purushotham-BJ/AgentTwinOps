from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from datetime import datetime
from typing import List, Optional

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.schemas.metric import MetricCreate, MetricResponse, MetricListResponse
from app.services.metric_service import MetricService

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.post("/", response_model=MetricResponse, status_code=status.HTTP_201_CREATED)
async def create_metric(
    metric: MetricCreate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    # Validate infrastructure exists
    infra_res = await db.execute(
        "SELECT id FROM infrastructure WHERE id = :sid",
        {"sid": metric.service_id},
    )
    if not infra_res.scalar():
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    metric_service = MetricService(db)
    created = await metric_service.ingest_metric(metric)
    return created

@router.get("/", response_model=MetricListResponse)
async def list_metrics(
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    metric_service = MetricService(db)
    metrics = await metric_service.list_metrics(skip, limit)
    return MetricListResponse(items=metrics, total=len(metrics))

@router.get("/service/{service_id}", response_model=MetricListResponse)
async def get_metrics_by_service(
    service_id: UUID,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = 100,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    metric_service = MetricService(db)
    metrics = await metric_service.get_metrics_by_service(
        service_id, start=start, end=end, limit=limit
    )
    return MetricListResponse(items=metrics, total=len(metrics))

@router.get("/service/{service_id}/latest", response_model=MetricResponse)
async def get_latest_metric(
    service_id: UUID,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    metric_service = MetricService(db)
    metric = await metric_service.get_latest_metric(service_id)
    if not metric:
        raise HTTPException(status_code=404, detail="No metrics found for service")
    return metric
