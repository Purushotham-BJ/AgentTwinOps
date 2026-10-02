"""Authenticated report export endpoints."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{report_type}")
async def export_report(
    report_type: Literal["infrastructure", "incidents", "predictions", "simulations"],
    session: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
) -> Response:
    service = ReportService(session)
    if report_type == "infrastructure":
        content = await service.infrastructure_csv()
    elif report_type == "incidents":
        content = await service.incidents_csv()
    elif report_type == "predictions":
        content = await service.predictions_csv()
    elif report_type == "simulations":
        content = await service.simulations_csv()
    else:
        raise HTTPException(status_code=404, detail="Report type is not available")

    date = datetime.now(timezone.utc).date().isoformat()
    filename = f"agenttwinops-{report_type}-report-{date}.csv"
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
