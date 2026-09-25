"""Backend-backed, non-persistent Digital Twin simulation service."""
from datetime import datetime, timedelta
from uuid import uuid4

from app.agents.simulation import SimulationAgent
from app.schemas.common import MetricPoint
from app.schemas.simulation import SimulationImpact, SimulationResult
from app.services.backend_client import backend_client


class SimulationService:
    def __init__(self) -> None:
        self.simulation_agent = SimulationAgent()

    async def _baseline(self, service_id: str, auth_token: str | None) -> dict:
        service = await backend_client.get_infrastructure_by_id(service_id, auth_token)
        if not service:
            raise ValueError("Infrastructure service not found")
        metrics = backend_client.get_metrics(service_id, limit=1, auth_token=auth_token)
        latest = metrics[-1] if metrics else {}
        return {
            "service_id": service_id,
            "service_name": service.get("service_name", service_id),
            "cpu_usage": float(latest.get("cpu_usage", 0.0)),
            "memory_usage": float(latest.get("memory_usage", 0.0)),
            "latency_ms": float(latest.get("latency", 0.0)),
            "status": service.get("status", "active"),
        }

    async def simulate(
        self,
        scenario: str,
        service_id: str,
        parameters: dict,
        horizon_minutes: int = 60,
        auth_token: str | None = None,
    ) -> SimulationResult:
        baseline = await self._baseline(service_id, auth_token)
        changes = dict(parameters or {})
        calculation = self.simulation_agent.simulate(baseline, scenario, changes)
        created_at = datetime.now()
        simulated = calculation["simulated"]
        timeline = [
            MetricPoint(
                timestamp=created_at + timedelta(minutes=horizon_minutes),
                value=simulated["cpu_usage"],
            )
        ]
        impact = SimulationImpact(
            cpu_delta=simulated["cpu_usage"] - calculation["baseline"]["cpu_usage"],
            memory_delta=simulated["memory_usage"] - calculation["baseline"]["memory_usage"],
            latency_delta=simulated["latency_ms"] - calculation["baseline"]["latency_ms"],
            failure_probability=calculation["simulated_failure_probability"],
        )
        return SimulationResult(
            id=str(uuid4()),
            scenario=scenario,
            service_id=service_id,
            status="completed",
            baseline_state=calculation["baseline"],
            scenario_changes=changes,
            simulated_state=simulated,
            simulated_health_score=calculation["simulated_health_score"],
            simulated_failure_probability=calculation["simulated_failure_probability"],
            simulated_operational_status=calculation["operational_status"],
            impact_summary=calculation["impact_summary"],
            predicted_impact=impact,
            timeline=timeline,
            recommendations=self.simulation_agent.recommendations(
                calculation["operational_status"]
            ),
            created_at=created_at,
            completed_at=created_at,
        )


simulation_service = SimulationService()
