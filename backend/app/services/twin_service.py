from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.metric import Metric
from app.models.twin import Twin, TwinHistory
from app.models.infrastructure import Infrastructure, InfrastructureStatus
from app.services.twin_utils import TwinUtils

class TwinService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_twin_by_service_id(self, service_id: UUID) -> Twin | None:
        stmt = select(Twin).where(Twin.service_id == service_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_twin_for_service(self, service_id: UUID) -> Twin:
        twin = Twin(service_id=service_id)
        self.session.add(twin)
        await self.session.flush()
        await self.session.refresh(twin)
        return twin

    def _calculate_health_score(self, metric: Metric, status: InfrastructureStatus) -> float:
        """Calculate health score based on metrics and infrastructure status."""
        if status in [InfrastructureStatus.INACTIVE, InfrastructureStatus.UNHEALTHY]:
            return 0.0

        score = 100.0
        
        # Penalize for high CPU
        if metric.cpu_usage > 90:
            score -= 30
        elif metric.cpu_usage > 70:
            score -= 10
            
        # Penalize for high memory
        if metric.memory_usage > 90:
            score -= 30
        elif metric.memory_usage > 70:
            score -= 10
            
        # Penalize for high latency
        if metric.latency > 1000:
            score -= 20
        elif metric.latency > 500:
            score -= 5
            
        return max(0.0, score)

    async def synchronize_twin(self, service_id: UUID, metric: Metric) -> Twin:
        """Synchronize a twin with the latest metric."""
        twin = await self.get_twin_by_service_id(service_id)
        if not twin:
            twin = await self.create_twin_for_service(service_id)

        # Get infrastructure for status
        stmt = select(Infrastructure).where(Infrastructure.id == service_id)
        result = await self.session.execute(stmt)
        infra = result.scalars().first()
        status = infra.status if infra else InfrastructureStatus.ACTIVE

        # Calculate health score
        health_score = self._calculate_health_score(metric, status)
        
        # Determine current state
        current_state = {
            "cpu": metric.cpu_usage,
            "memory": metric.memory_usage,
            "disk": metric.disk_usage,
            "network": metric.network_usage,
            "latency": metric.latency,
            "status": status.value
        }

        # Update twin
        twin.current_state = current_state
        twin.health_score = health_score
        
        # If health score is low, failure probability goes up
        twin.failure_probability = max(0.0, (100.0 - health_score) / 100.0)

        # New operational fields
        stale = await TwinUtils.is_metric_stale(metric.timestamp)
        operational_status = TwinUtils.calculate_operational_status(metric, status, stale)
        await TwinUtils.increment_state_version(twin)
        trends = await TwinUtils.calculate_trends(self.session, twin.id)
        anomalies = TwinUtils.detect_anomalies(metric)

        # Update twin with new fields
        twin.operational_status = operational_status
        twin.trends = trends
        twin.anomalies = anomalies

        # Create history record with additional fields
        history = TwinHistory(
            twin_id=twin.id,
            state=current_state,
            health_score=health_score,
            state_version=twin.state_version,
        )
        if hasattr(history, "trends"):
            setattr(history, "trends", trends)
        if hasattr(history, "anomalies"):
            setattr(history, "anomalies", anomalies)
        self.session.add(history)
        
        await self.session.flush()
        await self.session.refresh(twin)
        return twin

    async def update_predicted_state(
        self, service_id: UUID, predicted_state: Dict[str, Any]
    ) -> Twin:
        """Persist a new predicted_state on the twin without touching current_state.

        Called by the AI service after a successful ML prediction so the twin
        reflects the latest forecast.  All operational fields (health_score,
        operational_status, trends, anomalies, state_version) are left
        untouched — only ``predicted_state`` and ``last_sync`` are updated.
        """
        twin = await self.get_twin_by_service_id(service_id)
        if not twin:
            # Create a stub twin if one does not yet exist for this service.
            twin = await self.create_twin_for_service(service_id)

        # Stamp the payload with the persistence timestamp so consumers know
        # when this prediction was written to the database.
        predicted_state = dict(predicted_state)
        predicted_state["synced_at"] = datetime.now(timezone.utc).isoformat()

        twin.predicted_state = predicted_state
        twin.last_sync = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(twin)
        return twin
