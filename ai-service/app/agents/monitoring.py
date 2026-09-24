"""Monitoring Agent — analyzes current infrastructure state"""
from typing import Dict, Any
from .base import BaseAgent


class MonitoringAgent(BaseAgent):
    """
    Monitoring Agent
    
    Responsibilities:
    - Analyze current infrastructure metrics
    - Detect anomalies
    - Assess current health state
    """
    
    def __init__(self):
        super().__init__("MonitoringAgent")
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze infrastructure data and generate monitoring insights"""
        infrastructure = state.get("infrastructure_data", [])
        incidents = state.get("incident_data", [])
        
        # Analyze infrastructure health
        total_services = len(infrastructure)
        healthy_count = sum(1 for svc in infrastructure if svc.get("status") in ["healthy", "active"])
        degraded_count = sum(1 for svc in infrastructure if svc.get("status") == "degraded")
        unhealthy_count = sum(1 for svc in infrastructure if svc.get("status") in ["unhealthy", "inactive"])
        
        # Analyze incidents
        critical_incidents = [inc for inc in incidents if inc.get("severity") == "critical"]
        open_incidents = [inc for inc in incidents if inc.get("resolution_status") in ["open", "in_progress"]]
        
        analysis = {
            "infrastructure_health": {
                "total": total_services,
                "healthy": healthy_count,
                "degraded": degraded_count,
                "unhealthy": unhealthy_count,
                "health_percentage": (healthy_count / total_services * 100) if total_services > 0 else 0,
            },
            "incident_summary": {
                "total": len(incidents),
                "critical": len(critical_incidents),
                "open": len(open_incidents),
            },
            "anomalies_detected": degraded_count + unhealthy_count + len(critical_incidents),
            "requires_attention": degraded_count > 0 or unhealthy_count > 0 or len(critical_incidents) > 0,
        }
        
        state["monitoring_analysis"] = analysis
        return state
