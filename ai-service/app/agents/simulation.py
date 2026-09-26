"""Deterministic simulation calculations."""
from typing import Any, Dict, List


SCENARIO_DELTAS: Dict[str, Dict[str, float]] = {
    "cpu_spike": {"cpu_usage": 45.0, "memory_usage": 15.0, "latency_ms": 30.0},
    "traffic_surge": {"cpu_usage": 35.0, "memory_usage": 25.0, "latency_ms": 80.0},
    "database_failure": {"cpu_usage": 20.0, "memory_usage": 10.0, "latency_ms": 500.0},
    "pod_eviction": {"cpu_usage": 10.0, "memory_usage": -30.0, "latency_ms": 60.0},
    "custom": {},
}


class SimulationAgent:
    """Pure, deterministic what-if simulation engine."""

    def simulate(
        self, baseline: Dict[str, Any], scenario: str, changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        current = {
            "cpu_usage": float(baseline.get("cpu_usage", 0.0)),
            "memory_usage": float(baseline.get("memory_usage", 0.0)),
            "latency_ms": float(baseline.get("latency_ms", 0.0)),
            "status": baseline.get("status", "active"),
        }
        simulated = dict(current)
        deltas = SCENARIO_DELTAS[scenario]
        for field, delta in deltas.items():
            simulated[field] = delta + current[field]
        for field in ("cpu_usage", "memory_usage", "latency_ms"):
            if field in changes:
                simulated[field] = changes[field]
        if "status" in changes:
            simulated["status"] = changes["status"]
        simulated["cpu_usage"] = min(100.0, max(0.0, simulated["cpu_usage"]))
        simulated["memory_usage"] = min(100.0, max(0.0, simulated["memory_usage"]))
        simulated["latency_ms"] = max(0.0, simulated["latency_ms"])

        baseline_health = self.health_score(current)
        simulated_health = self.health_score(simulated)
        baseline_failure = self.failure_probability(current, baseline_health)
        simulated_failure = self.failure_probability(simulated, simulated_health)
        status = self.operational_status(simulated)
        summary = self.impact_summary(current, simulated, baseline_health, simulated_health)
        return {
            "baseline": current,
            "simulated": simulated,
            "baseline_health_score": baseline_health,
            "simulated_health_score": simulated_health,
            "baseline_failure_probability": baseline_failure,
            "simulated_failure_probability": simulated_failure,
            "operational_status": status,
            "impact_summary": summary,
        }

    @staticmethod
    def health_score(state: Dict[str, Any]) -> float:
        if state.get("status") in {"inactive", "unhealthy"}:
            return 0.0
        score = 100.0
        for value in (state["cpu_usage"], state["memory_usage"]):
            if value > 90:
                score -= 30
            elif value > 70:
                score -= 10
        if state["latency_ms"] > 1000:
            score -= 20
        elif state["latency_ms"] > 500:
            score -= 5
        return max(0.0, score)

    @staticmethod
    def failure_probability(state: Dict[str, Any], health: float) -> float:
        status_risk = {"inactive": 0.5, "unhealthy": 0.5, "degraded": 0.2}.get(
            state.get("status"), 0.0
        )
        return min(1.0, max(0.0, (100.0 - health) / 100.0 + status_risk))

    @staticmethod
    def operational_status(state: Dict[str, Any]) -> str:
        if state.get("status") in {"inactive", "unhealthy"}:
            return "CRITICAL"
        if (
            state["cpu_usage"] >= 90
            or state["memory_usage"] >= 90
            or state["latency_ms"] >= 1000
        ):
            return "CRITICAL"
        if (
            state["cpu_usage"] >= 70
            or state["memory_usage"] >= 70
            or state["latency_ms"] >= 500
            or state.get("status") == "degraded"
        ):
            return "WARNING"
        return "HEALTHY"

    @staticmethod
    def impact_summary(
        baseline: Dict[str, Any],
        simulated: Dict[str, Any],
        baseline_health: float,
        simulated_health: float,
    ) -> List[str]:
        summary: List[str] = []
        if simulated["cpu_usage"] != baseline["cpu_usage"]:
            summary.append("CPU usage changed in the simulated state.")
        if simulated["memory_usage"] != baseline["memory_usage"]:
            summary.append("Memory usage changed in the simulated state.")
        if simulated["latency_ms"] != baseline["latency_ms"]:
            summary.append("Latency changed in the simulated state.")
        if simulated["status"] != baseline["status"]:
            summary.append("Infrastructure status changed in the simulated state.")
        if simulated_health < baseline_health:
            summary.append("Simulated health decreased.")
        if not summary:
            summary.append("Scenario does not change the baseline state.")
        return summary

    @staticmethod
    def recommendations(status: str) -> List[str]:
        if status == "CRITICAL":
            return ["Investigate the simulated critical condition before applying it."]
        if status == "WARNING":
            return ["Monitor the affected resource and prepare mitigation."]
        return ["Continue normal monitoring."]
