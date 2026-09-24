"""Simulation Agent — runs what-if scenarios"""
from typing import Dict, Any
from datetime import datetime, timedelta
from .base import BaseAgent


SCENARIO_CONFIGS = {
    "cpu_spike": {"cpu_delta": 45, "mem_delta": 15, "lat_delta": 30, "failure_impact": 0.5},
    "traffic_surge": {"cpu_delta": 35, "mem_delta": 25, "lat_delta": 80, "failure_impact": 0.4},
    "database_failure": {"cpu_delta": 20, "mem_delta": 10, "lat_delta": 500, "failure_impact": 0.8},
    "pod_eviction": {"cpu_delta": 10, "mem_delta": -30, "lat_delta": 60, "failure_impact": 0.6},
}


class SimulationAgent(BaseAgent):
    """
    Simulation Agent
    
    Responsibilities:
    - Run what-if scenarios
    - Model infrastructure behavior under stress
    - Generate impact predictions
    """
    
    def __init__(self):
        super().__init__("SimulationAgent")
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simulation scenario"""
        scenario = state.get("scenario", "cpu_spike")
        service_id = state.get("service_id")
        
        config = SCENARIO_CONFIGS.get(scenario, SCENARIO_CONFIGS["cpu_spike"])
        
        # Generate impact analysis
        impact = {
            "cpu_delta": config["cpu_delta"] + (hash(service_id) % 10 - 5),
            "memory_delta": config["mem_delta"] + (hash(service_id) % 10 - 5),
            "latency_delta": config["lat_delta"] + (hash(service_id) % 20 - 10),
            "failure_probability": min(0.95, config["failure_impact"] + (hash(service_id) % 10) * 0.03),
        }
        
        # Generate timeline (20 points over 60 minutes)
        timeline = []
        now = datetime.now()
        for i in range(20):
            phase = i / 20
            # Impact curve: ramps up, peaks, then declines
            if phase < 0.3:
                intensity = phase / 0.3
            elif phase < 0.6:
                intensity = 1.0
            else:
                intensity = (1 - phase) / 0.4
            
            timeline.append({
                "timestamp": (now + timedelta(minutes=i * 3)).isoformat(),
                "value": max(0, min(100, 30 + config["cpu_delta"] * intensity)),
            })
        
        # Generate recommendations using LLM if available
        if self.llm:
            try:
                from langchain_core.prompts import ChatPromptTemplate
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are an infrastructure resilience expert. Provide mitigation recommendations."),
                    ("user", f"Scenario: {scenario}. CPU impact: +{impact['cpu_delta']}%, Latency: +{impact['latency_delta']}ms. What actions should be taken?"),
                ])
                response = await self.llm.ainvoke(prompt.format_messages())
                recommendations = [line.strip() for line in response.content.split("\n") if line.strip() and len(line) > 10][:4]
            except:
                recommendations = self._get_default_recommendations(scenario)
        else:
            recommendations = self._get_default_recommendations(scenario)
        
        result = {
            "impact": impact,
            "timeline": timeline,
            "recommendations": recommendations,
        }
        
        state["simulation_result"] = result
        return state
    
    def _get_default_recommendations(self, scenario: str) -> list:
        """Default recommendations by scenario"""
        base = [
            "Pre-scale service to handle projected load",
            "Enable auto-scaling policies with lower thresholds",
            "Set up circuit breakers for downstream dependencies",
            "Increase health check frequency during scenario window",
        ]
        return base
