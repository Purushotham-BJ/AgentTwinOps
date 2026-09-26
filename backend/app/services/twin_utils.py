import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any

from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.twin import Twin, TwinHistory
from app.models.metric import Metric
from app.models.infrastructure import Infrastructure, InfrastructureStatus
from app.config.settings import get_settings

# Thresholds (could be moved to settings if needed)
CPU_WARNING_THRESHOLD = 70.0
CPU_DEGRADED_THRESHOLD = 90.0
MEMORY_WARNING_THRESHOLD = 70.0
MEMORY_DEGRADED_THRESHOLD = 90.0
LATENCY_WARNING_THRESHOLD = 500.0  # ms
LATENCY_DEGRADED_THRESHOLD = 1000.0  # ms

TREND_WINDOW = 5  # number of recent history points to consider
TREND_TOLERANCE = 5.0  # percent change considered stable

ANOMALY_THRESHOLDS = {
    "HIGH_CPU": CPU_DEGRADED_THRESHOLD,
    "HIGH_MEMORY": MEMORY_DEGRADED_THRESHOLD,
    "HIGH_DISK": 90.0,
    "HIGH_LATENCY": LATENCY_DEGRADED_THRESHOLD,
}

class TwinUtils:
    @staticmethod
    async def is_metric_stale(metric_timestamp: datetime) -> bool:
        settings = get_settings()
        now = datetime.now(timezone.utc)
        age = (now - metric_timestamp).total_seconds()
        return age > settings.METRIC_STALE_THRESHOLD

    @staticmethod
    def calculate_operational_status(metric: Metric, infra_status: InfrastructureStatus, stale: bool) -> str:
        # Unknown if metric missing
        if metric is None:
            return "UNKNOWN"
        if stale:
            return "STALE"
        # Determine status based on thresholds
        cpu = metric.cpu_usage
        mem = metric.memory_usage
        latency = metric.latency
        # Simple hierarchy: CRITICAL > DEGRADED > WARNING > HEALTHY
        if (
            cpu >= CPU_DEGRADED_THRESHOLD
            or mem >= MEMORY_DEGRADED_THRESHOLD
            or latency >= LATENCY_DEGRADED_THRESHOLD
            or infra_status in [InfrastructureStatus.UNHEALTHY, InfrastructureStatus.INACTIVE]
        ):
            return "CRITICAL"
        if (
            cpu >= CPU_WARNING_THRESHOLD
            or mem >= MEMORY_WARNING_THRESHOLD
            or latency >= LATENCY_WARNING_THRESHOLD
        ):
            return "WARNING"
        return "HEALTHY"

    @staticmethod
    async def calculate_trends(session: AsyncSession, twin_id: uuid.UUID) -> Dict[str, str]:
        # Retrieve recent history entries
        stmt = (
            select(TwinHistory)
            .where(TwinHistory.twin_id == twin_id)
            .order_by(desc(TwinHistory.timestamp))
            .limit(TREND_WINDOW)
        )
        results = await session.execute(stmt)
        histories: List[TwinHistory] = results.scalars().all()
        if len(histories) < 2:
            return {"cpu": "INSUFFICIENT_DATA", "memory": "INSUFFICIENT_DATA", "health": "INSUFFICIENT_DATA"}
        # Compute simple trend based on average of first half vs second half
        mids = len(histories) // 2
        first = histories[mids:]
        second = histories[:mids]
        def avg(attr: str) -> float:
            vals = [getattr(h.state, attr, 0) if isinstance(h.state, dict) else 0 for h in first]
            return sum(vals) / len(vals) if vals else 0.0
        def avg_second(attr: str) -> float:
            vals = [getattr(h.state, attr, 0) if isinstance(h.state, dict) else 0 for h in second]
            return sum(vals) / len(vals) if vals else 0.0
        trends: Dict[str, str] = {}
        for key in ["cpu", "memory", "health_score"]:
            avg1 = avg(key)
            avg2 = avg_second(key)
            if avg2 == 0:
                trends[key] = "INSUFFICIENT_DATA"
                continue
            change = ((avg1 - avg2) / avg2) * 100.0
            if abs(change) <= TREND_TOLERANCE:
                trends[key] = "STABLE"
            elif change > 0:
                trends[key] = "INCREASING"
            else:
                trends[key] = "DECREASING"
        return trends

    @staticmethod
    def detect_anomalies(metric: Metric) -> List[Dict[str, Any]]:
        anomalies: List[Dict[str, Any]] = []
        for name, threshold in ANOMALY_THRESHOLDS.items():
            if name == "HIGH_CPU" and metric.cpu_usage > threshold:
                anomalies.append({"type": name, "value": metric.cpu_usage, "threshold": threshold, "severity": "WARNING"})
            if name == "HIGH_MEMORY" and metric.memory_usage > threshold:
                anomalies.append({"type": name, "value": metric.memory_usage, "threshold": threshold, "severity": "WARNING"})
            if name == "HIGH_DISK" and metric.disk_usage > threshold:
                anomalies.append({"type": name, "value": metric.disk_usage, "threshold": threshold, "severity": "WARNING"})
            if name == "HIGH_LATENCY" and metric.latency > threshold:
                anomalies.append({"type": name, "value": metric.latency, "threshold": threshold, "severity": "WARNING"})
        return anomalies

    @staticmethod
    async def increment_state_version(twin: Twin) -> None:
        twin.state_version += 1
