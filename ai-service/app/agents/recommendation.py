"""Deterministic, explainable recommendation rules."""
from typing import Any, Dict, List


PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class RecommendationAgent:
    """Evaluate one service's operational state without side effects."""

    def generate(
        self,
        service: Dict[str, Any],
        metric: Dict[str, Any],
        twin: Dict[str, Any] | None,
        incidents: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        current = (twin or {}).get("current_state") or {}
        cpu = float(current.get("cpu", current.get("cpu_usage", metric.get("cpu_usage", 0))))
        memory = float(current.get("memory", current.get("memory_usage", metric.get("memory_usage", 0))))
        latency = float(current.get("latency", current.get("latency_ms", metric.get("latency", 0))))
        status = str((twin or {}).get("operational_status", service.get("status", "active"))).lower()
        health = float((twin or {}).get("health_score", 100))
        failure = float((twin or {}).get("failure_probability", 0))
        service_id = str(service["id"])
        name = service.get("service_name", service_id)
        recommendations: List[Dict[str, Any]] = []

        if cpu >= 90:
            recommendations.append(self._make(service_id, name, "CPU_OPTIMIZATION", "Scale compute resources", "CPU usage is critically elevated.", "Reduce CPU workload or scale compute resources.", "high", "scaling", 0.95))
        elif cpu >= 70:
            recommendations.append(self._make(service_id, name, "CPU_OPTIMIZATION", "Optimize CPU workload", "CPU usage is elevated.", "Reduce CPU workload and review compute allocation.", "medium", "optimization", 0.85))
        if memory >= 90:
            recommendations.append(self._make(service_id, name, "MEMORY_OPTIMIZATION", "Increase memory allocation", "Memory usage is critically elevated.", "Investigate memory pressure and increase memory allocation.", "high", "scaling", 0.95))
        elif memory >= 70:
            recommendations.append(self._make(service_id, name, "MEMORY_OPTIMIZATION", "Investigate memory pressure", "Memory usage is elevated.", "Inspect memory growth and consider increasing allocation.", "medium", "optimization", 0.85))
        if latency >= 1000:
            recommendations.append(self._make(service_id, name, "LATENCY_OPTIMIZATION", "Reduce request latency", "Latency is critically elevated.", "Investigate network and database bottlenecks immediately.", "high", "optimization", 0.95))
        elif latency >= 500:
            recommendations.append(self._make(service_id, name, "LATENCY_OPTIMIZATION", "Investigate high latency", "Latency is elevated.", "Investigate network and database bottlenecks.", "medium", "optimization", 0.85))
        if failure >= 0.7:
            recommendations.append(self._make(service_id, name, "FAILURE_PREVENTION", "Investigate predicted failure", f"Failure probability is {failure:.0%}.", "Prioritize investigation and recovery actions for the service.", "critical", "reliability", 0.95))
        elif failure >= 0.4:
            recommendations.append(self._make(service_id, name, "FAILURE_PREVENTION", "Prepare failure mitigation", f"Failure probability is {failure:.0%}.", "Review recovery procedures and monitor the service closely.", "high", "reliability", 0.85))
        if status in {"critical", "unhealthy", "inactive"} or health < 50:
            recommendations.append(self._make(service_id, name, "INCIDENT_RESPONSE", "Investigate critical service state", f"Operational status is {status} with health score {health:.0f}.", "Investigate the service and restore healthy operation.", "critical", "reliability", 0.98))
        elif status in {"warning", "degraded"} or health < 75:
            recommendations.append(self._make(service_id, name, "INVESTIGATION", "Investigate degraded service", f"Operational status is {status} with health score {health:.0f}.", "Investigate the detected degradation and monitor recovery.", "high", "reliability", 0.9))
        if incidents:
            critical = any(str(i.get("severity", "")).lower() in {"critical", "high"} for i in incidents)
            recommendations.append(self._make(service_id, name, "INCIDENT_RESPONSE", "Review open incidents", "Open incidents are associated with this service.", "Resolve the highest-severity incident and verify service recovery.", "critical" if critical else "high", "reliability", 0.95 if critical else 0.85))
        anomalies = (twin or {}).get("anomalies") or []
        if anomalies:
            recommendations.append(self._make(service_id, name, "INVESTIGATION", "Investigate detected anomaly", f"{len(anomalies)} anomaly signal(s) are present in the Digital Twin.", "Inspect the anomaly evidence and confirm whether remediation is required.", "high", "reliability", 0.9))

        deduped: Dict[str, Dict[str, Any]] = {}
        for item in recommendations:
            deduped[item["type"]] = item
        return sorted(deduped.values(), key=lambda item: (PRIORITY_ORDER[item["priority"]], item["type"]))

    @staticmethod
    def _make(service_id: str, name: str, kind: str, title: str, reason: str, action: str, priority: str, category: str, confidence: float) -> Dict[str, Any]:
        return {
            "id": f"{service_id}:{kind}",
            "service_id": service_id,
            "service_name": name,
            "type": kind,
            "title": title,
            "description": reason,
            "reason": reason,
            "action": action,
            "priority": priority,
            "severity": priority,
            "expected_impact": action,
            "implementation_steps": [action],
            "category": category,
            "estimated_effort": "low" if priority == "critical" else "medium",
            "confidence": confidence,
            "source": "rule",
        }
