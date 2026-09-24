"""Recovery Agent — suggests recovery actions"""
from typing import Dict, Any, List
from .base import BaseAgent
from langchain_core.prompts import ChatPromptTemplate


class RecoveryAgent(BaseAgent):
    """
    Recovery Agent
    
    Responsibilities:
    - Analyze failure scenarios
    - Generate recovery strategies
    - Prioritize actions
    """
    
    def __init__(self):
        super().__init__("RecoveryAgent")
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recovery recommendations"""
        monitoring = state.get("monitoring_analysis", {})
        prediction = state.get("prediction_analysis", {})
        simulation = state.get("simulation_result", {})
        
        recommendations = []
        
        # Analyze monitoring data
        if monitoring:
            health = monitoring.get("infrastructure_health", {})
            unhealthy = health.get("unhealthy", 0)
            degraded = health.get("degraded", 0)
            
            if unhealthy > 0:
                recommendations.append({
                    "action": "Restart unhealthy services",
                    "priority": "critical",
                    "impact": "Restore service availability",
                    "steps": [
                        "Identify root cause from logs",
                        "Perform rolling restart",
                        "Verify health checks pass",
                    ]
                })
            
            if degraded > 0:
                recommendations.append({
                    "action": "Scale degraded services",
                    "priority": "high",
                    "impact": "Prevent cascading failures",
                    "steps": [
                        "Add replica instances",
                        "Monitor resource utilization",
                        "Gradually shift traffic",
                    ]
                })
        
        # Analyze predictions
        if prediction:
            failure_prob = prediction.get("failure_probability", 0)
            predicted_value = prediction.get("predicted_value", 0)
            
            if failure_prob > 0.5:
                recommendations.append({
                    "action": "Pre-emptive scaling",
                    "priority": "critical",
                    "impact": f"Reduce failure risk from {failure_prob*100:.0f}% to <30%",
                    "steps": [
                        "Scale horizontal replicas to 3x",
                        "Increase memory limits by 50%",
                        "Enable circuit breakers",
                    ]
                })
            elif failure_prob > 0.3:
                recommendations.append({
                    "action": "Resource optimization",
                    "priority": "medium",
                    "impact": "Improve headroom and stability",
                    "steps": [
                        "Review and optimize queries",
                        "Implement caching layer",
                        "Tune GC parameters",
                    ]
                })
        
        # Analyze simulation
        if simulation:
            impact = simulation.get("impact", {})
            sim_failure_prob = impact.get("failure_probability", 0)
            
            if sim_failure_prob > 0.6:
                recommendations.append({
                    "action": "Infrastructure hardening",
                    "priority": "high",
                    "impact": "Build resilience against scenario",
                    "steps": [
                        "Add redundancy to critical path",
                        "Implement graceful degradation",
                        "Configure rate limiting",
                    ]
                })
        
        # If LLM available, enhance recommendations
        if self.llm and recommendations:
            try:
                context = {
                    "monitoring": monitoring,
                    "prediction": prediction,
                    "current_recs": [r["action"] for r in recommendations],
                }
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are an SRE expert. Enhance recovery recommendations with specific technical details."),
                    ("user", f"Context: {context}. Current recommendations: {recommendations[0]['action']}. Provide 2 additional actionable steps."),
                ])
                response = await self.llm.ainvoke(prompt.format_messages())
                # Add AI-enhanced recommendation
                ai_steps = [line.strip() for line in response.content.split("\n") if line.strip()][:2]
                if ai_steps:
                    recommendations.append({
                        "action": "AI-recommended mitigation",
                        "priority": "medium",
                        "impact": "Additional risk reduction",
                        "steps": ai_steps,
                    })
            except:
                pass
        
        state["recovery_recommendations"] = recommendations
        return state
