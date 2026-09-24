"""Recommendation Agent — generates prioritized recommendations"""
from typing import Dict, Any, List
from datetime import datetime
from .base import BaseAgent
from langchain_core.prompts import ChatPromptTemplate


class RecommendationAgent(BaseAgent):
    """
    Recommendation Agent
    
    Responsibilities:
    - Synthesize insights from all agents
    - Generate prioritized recommendations
    - Format output for dashboard
    """
    
    def __init__(self):
        super().__init__("RecommendationAgent")
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final recommendations"""
        recovery_recs = state.get("recovery_recommendations", [])
        monitoring = state.get("monitoring_analysis", {})
        prediction = state.get("prediction_analysis", {})
        
        recommendations = []
        
        # Process recovery recommendations
        for rec in recovery_recs:
            recommendations.append({
                "id": f"rec_{hash(rec['action']) % 10000:04d}",
                "service_id": state.get("service_id"),
                "service_name": f"Service {state.get('service_id', 'unknown')[-4:]}",
                "title": rec["action"],
                "description": rec["impact"],
                "priority": rec["priority"],
                "severity": rec["priority"],
                "expected_impact": rec["impact"],
                "implementation_steps": rec["steps"],
                "category": self._categorize(rec["action"]),
                "estimated_effort": self._estimate_effort(rec["action"]),
                "created_at": datetime.now().isoformat(),
                "source": "ai",
            })
        
        # Add cost optimization recommendations
        if monitoring:
            health = monitoring.get("infrastructure_health", {})
            if health.get("healthy", 0) == health.get("total", 0) and health.get("total", 0) > 0:
                recommendations.append({
                    "id": f"rec_cost_{hash(str(monitoring)) % 10000:04d}",
                    "service_id": None,
                    "service_name": "All Services",
                    "title": "Optimize resource allocation",
                    "description": "All services healthy - opportunity for resource optimization",
                    "priority": "low",
                    "severity": "low",
                    "expected_impact": "10-20% cost reduction without service impact",
                    "implementation_steps": [
                        "Review CPU and memory requests vs actual usage",
                        "Right-size container resources",
                        "Enable cluster autoscaling",
                        "Implement pod disruption budgets",
                    ],
                    "category": "cost",
                    "estimated_effort": "medium",
                    "created_at": datetime.now().isoformat(),
                    "source": "ai",
                })
        
        # Add monitoring recommendations if AI available
        if self.llm and len(recommendations) < 3:
            try:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are a cloud infrastructure expert. Generate ONE specific, actionable recommendation."),
                    ("user", f"Infrastructure state: {monitoring}. Suggest one proactive improvement focusing on reliability or security."),
                ])
                response = await self.llm.ainvoke(prompt.format_messages())
                
                recommendations.append({
                    "id": f"rec_ai_{hash(response.content) % 10000:04d}",
                    "service_id": None,
                    "service_name": "Infrastructure",
                    "title": "AI-suggested improvement",
                    "description": response.content[:200],
                    "priority": "medium",
                    "severity": "medium",
                    "expected_impact": "Enhanced system reliability",
                    "implementation_steps": [
                        line.strip() for line in response.content.split("\n") 
                        if line.strip() and len(line) > 10
                    ][:3],
                    "category": "reliability",
                    "estimated_effort": "medium",
                    "created_at": datetime.now().isoformat(),
                    "source": "ai",
                })
            except:
                pass
        
        state["recommendations"] = recommendations
        return state
    
    def _categorize(self, action: str) -> str:
        """Categorize recommendation"""
        action_lower = action.lower()
        if "scale" in action_lower or "replica" in action_lower:
            return "scaling"
        elif "security" in action_lower or "access" in action_lower:
            return "security"
        elif "cost" in action_lower or "optimize" in action_lower:
            return "cost"
        elif "restart" in action_lower or "recovery" in action_lower:
            return "reliability"
        else:
            return "optimization"
    
    def _estimate_effort(self, action: str) -> str:
        """Estimate implementation effort"""
        action_lower = action.lower()
        if "restart" in action_lower or "scale" in action_lower:
            return "low"
        elif "optimize" in action_lower or "configure" in action_lower:
            return "medium"
        else:
            return "high"
