"""Deterministic coordinator for the multi-agent operations workflow."""
from typing import Any, Dict, List

from app.agents.monitoring import MonitoringAgent
from app.agents.prediction import PredictionAgent
from app.agents.recommendation import RecommendationAgent
from app.agents.simulation import SimulationAgent
from app.agents.recovery import RecoveryAgent
from app.schemas.orchestration import AgentExecution, OrchestrationResponse
from app.services.backend_client import backend_client
from app.services.simulation_service import simulation_service


class OrchestrationService:
    def __init__(self) -> None:
        self.monitoring_agent = MonitoringAgent()
        self.prediction_agent = PredictionAgent()
        self.recommendation_agent = RecommendationAgent()
        self.simulation_agent = SimulationAgent()
        self.recovery_agent = RecoveryAgent()

    async def orchestrate(
        self,
        service_id: str,
        include_prediction: bool = True,
        include_simulation: bool = True,
        include_recovery: bool = True,
        horizon_minutes: int = 360,
        auth_token: str | None = None,
    ) -> OrchestrationResponse:
        service = await backend_client.get_infrastructure_by_id(service_id, auth_token)
        if not service:
            raise ValueError("Infrastructure service not found")
        metrics = backend_client.get_metrics(service_id, limit=1, auth_token=auth_token)
        incidents = await backend_client.get_incidents(auth_token=auth_token)
        twin = await backend_client.get_twin_by_service(service_id, auth_token)
        latest_metric = metrics[-1] if metrics else {}
        service_incidents = [i for i in incidents if str(i.get("service_id")) == service_id]
        executions: List[AgentExecution] = []
        errors: List[str] = []

        monitoring_state = await self.monitoring_agent.process({
            "infrastructure_data": [service],
            "incident_data": service_incidents,
        })
        monitoring = {
            **monitoring_state.get("monitoring_analysis", {}),
            "service": service,
            "latest_metric": latest_metric,
            "twin": twin,
            "incidents": service_incidents,
            "operational_status": self._operational_status(service, twin, latest_metric),
        }
        executions.append(AgentExecution(agent="monitoring", status="SUCCESS"))
        predictions: Dict[str, Any] = {}
        if include_prediction:
            try:
                prediction_state = {
                    "service_id": service_id,
                    "prediction_type": "failure",
                    "horizon_minutes": horizon_minutes,
                    "monitoring_analysis": monitoring,
                }
                predictions["failure"] = (await self.prediction_agent.process(prediction_state)).get(
                    "prediction_analysis", {}
                )
                executions.append(AgentExecution(agent="prediction", status="SUCCESS"))
            except Exception as exc:
                executions.append(AgentExecution(agent="prediction", status="FAILED", error="prediction failed"))
                errors.append("prediction failed")
        else:
            executions.append(AgentExecution(agent="prediction", status="SKIPPED"))

        recommendations: List[Dict[str, Any]] = []
        try:
            recommendations = self.recommendation_agent.generate(
                service, latest_metric, twin, service_incidents
            )
            executions.append(AgentExecution(agent="recommendation", status="SUCCESS"))
        except Exception:
            executions.append(AgentExecution(agent="recommendation", status="FAILED", error="recommendation failed"))
            errors.append("recommendation failed")

        simulations: List[Dict[str, Any]] = []
        operational_status = self._operational_status(service, twin, latest_metric)
        should_simulate = include_simulation and operational_status in {"WARNING", "CRITICAL"}
        if should_simulate:
            try:
                result = await simulation_service.simulate(
                    scenario="custom",
                    service_id=service_id,
                    parameters=self._simulation_parameters(latest_metric, service),
                    horizon_minutes=horizon_minutes,
                    auth_token=auth_token,
                )
                simulations.append(result.model_dump(mode="json"))
                executions.append(AgentExecution(agent="simulation", status="SUCCESS"))
            except Exception:
                executions.append(AgentExecution(agent="simulation", status="FAILED", error="simulation failed"))
                errors.append("simulation failed")
        else:
            executions.append(AgentExecution(agent="simulation", status="SKIPPED"))

        recovery_actions: List[Dict[str, Any]] = []
        if include_recovery:
            recovery_state = await self.recovery_agent.process({
                "operational_status": operational_status,
                "recommendations": recommendations,
            })
            recovery_actions = recovery_state.get("recovery_recommendations", [])
            executions.append(AgentExecution(agent="recovery", status="SUCCESS"))
        else:
            executions.append(AgentExecution(agent="recovery", status="SKIPPED"))

        failure_probability = float(
            (twin or {}).get("failure_probability", predictions.get("failure", {}).get("failure_probability", 0.0))
        )
        health_score = float((twin or {}).get("health_score", self._health_from_metric(latest_metric)))
        return OrchestrationResponse(
            service_id=service_id,
            status="FAILED" if errors and not recommendations else "SUCCESS",
            operational_status=operational_status,
            health_score=health_score,
            failure_probability=failure_probability,
            agents=executions,
            monitoring=monitoring,
            predictions=predictions,
            recommendations=recommendations,
            simulations=simulations,
            recovery_actions=recovery_actions,
            errors=errors,
        )

    @staticmethod
    def _operational_status(service: Dict[str, Any], twin: Dict[str, Any] | None, metric: Dict[str, Any]) -> str:
        status = str((twin or {}).get("operational_status", service.get("status", "active"))).lower()
        cpu = float(metric.get("cpu_usage", 0))
        memory = float(metric.get("memory_usage", 0))
        latency = float(metric.get("latency", 0))
        if status in {"critical", "unhealthy", "inactive"} or cpu >= 90 or memory >= 90 or latency >= 1000:
            return "CRITICAL"
        if status in {"warning", "degraded"} or cpu >= 70 or memory >= 70 or latency >= 500:
            return "WARNING"
        return "HEALTHY"

    @staticmethod
    def _health_from_metric(metric: Dict[str, Any]) -> float:
        penalties = sum(10 if value >= 70 else 0 for value in (
            float(metric.get("cpu_usage", 0)), float(metric.get("memory_usage", 0))
        ))
        return max(0.0, 100.0 - penalties)

    @staticmethod
    def _simulation_parameters(metric: Dict[str, Any], service: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "cpu_usage": float(metric.get("cpu_usage", 0)),
            "memory_usage": float(metric.get("memory_usage", 0)),
            "latency_ms": float(metric.get("latency", 0)),
            "status": service.get("status", "active"),
        }

orchestration_service = OrchestrationService()
