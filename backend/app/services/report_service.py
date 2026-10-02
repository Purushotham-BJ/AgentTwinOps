"""Generate downloadable reports from persisted AgentTwinOps data."""
from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident
from app.models.infrastructure import Infrastructure
from app.models.metric import Metric
from app.models.twin import Twin
from app.models.prediction import PredictionHistory
from app.models.simulation import SimulationHistory


def _csv_response(rows: Iterable[dict[str, object]], fieldnames: list[str]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def _value(value: object) -> object:
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    return value


class ReportService:
    """Build CSV exports using only persisted infrastructure data."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def infrastructure_csv(self) -> bytes:
        ranked_metrics = (
            select(
                Metric,
                func.row_number()
                .over(
                    partition_by=Metric.service_id,
                    order_by=Metric.timestamp.desc(),
                )
                .label("metric_rank"),
            )
            .subquery()
        )
        latest_metric = aliased(Metric, ranked_metrics)
        query = (
            select(Infrastructure, latest_metric, Twin)
            .join(
                latest_metric,
                (latest_metric.service_id == Infrastructure.id)
                & (ranked_metrics.c.metric_rank == 1),
                isouter=True,
            )
            .join(Twin, Twin.service_id == Infrastructure.id, isouter=True)
            .order_by(Infrastructure.service_name)
        )
        result = await self.session.execute(query)
        rows = []
        for infra, metric, twin in result.unique().all():
            rows.append(
                {
                    "service_id": str(infra.id),
                    "service_name": infra.service_name,
                    "service_type": infra.service_type,
                    "host": infra.host,
                    "status": _value(infra.status),
                    "updated_at": _value(infra.updated_at),
                    "latest_metric_timestamp": _value(metric.timestamp) if metric else "",
                    "cpu_usage": metric.cpu_usage if metric else "",
                    "memory_usage": metric.memory_usage if metric else "",
                    "disk_usage": metric.disk_usage if metric else "",
                    "network_usage": metric.network_usage if metric else "",
                    "latency": metric.latency if metric else "",
                    "twin_health_score": twin.health_score if twin else "",
                    "twin_failure_probability": twin.failure_probability if twin else "",
                    "twin_operational_status": _value(twin.operational_status) if twin else "",
                    "twin_last_sync": _value(twin.last_sync) if twin else "",
                }
            )
        return _csv_response(
            rows,
            [
                "service_id",
                "service_name",
                "service_type",
                "host",
                "status",
                "updated_at",
                "latest_metric_timestamp",
                "cpu_usage",
                "memory_usage",
                "disk_usage",
                "network_usage",
                "latency",
                "twin_health_score",
                "twin_failure_probability",
                "twin_operational_status",
                "twin_last_sync",
            ],
        )

    async def incidents_csv(self) -> bytes:
        query = (
            select(Incident, Infrastructure.service_name)
            .join(Infrastructure, Infrastructure.id == Incident.service_id)
            .order_by(Incident.timestamp.desc())
        )
        result = await self.session.execute(query)
        rows = [
            {
                "incident_id": str(incident.id),
                "service_id": str(incident.service_id),
                "service_name": service_name,
                "severity": _value(incident.severity),
                "incident_type": incident.incident_type,
                "resolution_status": _value(incident.resolution_status),
                "timestamp": _value(incident.timestamp),
                "created_at": _value(incident.created_at),
                "updated_at": _value(incident.updated_at),
            }
            for incident, service_name in result.all()
        ]
        return _csv_response(
            rows,
            [
                "incident_id",
                "service_id",
                "service_name",
                "severity",
                "incident_type",
                "resolution_status",
                "timestamp",
                "created_at",
                "updated_at",
            ],
        )

    async def predictions_csv(self) -> bytes:
        query = (
            select(PredictionHistory, Infrastructure.service_name)
            .join(Infrastructure, Infrastructure.id == PredictionHistory.service_id)
            .order_by(PredictionHistory.created_at.desc())
        )
        result = await self.session.execute(query)
        rows = []
        for prediction, service_name in result.all():
            rows.append({
                "prediction_id": str(prediction.id),
                "service_id": str(prediction.service_id),
                "service_name": service_name,
                "prediction_type": prediction.prediction_type,
                "predicted_value": prediction.predicted_value,
                "confidence": prediction.confidence,
                "failure_probability": prediction.failure_probability,
                "risk_level": prediction.risk_level,
                "status": prediction.status,
                "horizon_minutes": prediction.horizon_minutes,
                "prediction_source": prediction.prediction_source,
                "recommended_action": prediction.recommended_action,
                "created_at": _value(prediction.created_at),
            })
        return _csv_response(rows, [
            "prediction_id", "service_id", "service_name", "prediction_type",
            "predicted_value", "confidence", "failure_probability", "risk_level",
            "status", "horizon_minutes", "prediction_source", "recommended_action",
            "created_at",
        ])

    async def simulations_csv(self) -> bytes:
        query = (
            select(SimulationHistory, Infrastructure.service_name)
            .join(Infrastructure, Infrastructure.id == SimulationHistory.service_id)
            .order_by(SimulationHistory.created_at.desc())
        )
        result = await self.session.execute(query)
        rows = []
        for simulation, service_name in result.all():
            rows.append({
                "simulation_id": str(simulation.id),
                "service_id": str(simulation.service_id),
                "service_name": service_name,
                "scenario": simulation.scenario,
                "status": simulation.status,
                "simulated_health_score": simulation.simulated_health_score,
                "simulated_failure_probability": simulation.simulated_failure_probability,
                "simulated_operational_status": simulation.simulated_operational_status,
                "created_at": _value(simulation.created_at),
                "completed_at": _value(simulation.completed_at) if simulation.completed_at else "",
            })
        return _csv_response(rows, [
            "simulation_id", "service_id", "service_name", "scenario", "status",
            "simulated_health_score", "simulated_failure_probability",
            "simulated_operational_status", "created_at", "completed_at",
        ])
