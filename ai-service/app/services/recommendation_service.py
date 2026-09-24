"""Recommendation service with LangGraph orchestration"""
from typing import List
from datetime import datetime
from langgraph.graph import StateGraph, END
from app.orchestration.state import RecommendationState
from app.agents import MonitoringAgent, PredictionAgent, RecoveryAgent, RecommendationAgent
from app.services.backend_client import backend_client
from app.schemas.recommendation import Recommendation


class RecommendationService:
    """Service for generating AI recommendations"""
    
    def __init__(self):
        self.monitoring_agent = MonitoringAgent()
        self.prediction_agent = PredictionAgent()
        self.recovery_agent = RecoveryAgent()
        self.recommendation_agent = RecommendationAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph for recommendation workflow"""
        workflow = StateGraph(RecommendationState)
        
        # Add nodes
        workflow.add_node("monitoring", self._monitoring_node)
        workflow.add_node("prediction", self._prediction_node)
        workflow.add_node("recovery", self._recovery_node)
        workflow.add_node("recommendation", self._recommendation_node)
        
        # Define edges
        workflow.set_entry_point("monitoring")
        workflow.add_edge("monitoring", "prediction")
        workflow.add_edge("prediction", "recovery")
        workflow.add_edge("recovery", "recommendation")
        workflow.add_edge("recommendation", END)
        
        return workflow.compile()
    
    async def _monitoring_node(self, state: RecommendationState) -> RecommendationState:
        """Monitoring analysis"""
        infrastructure = await backend_client.get_infrastructure()
        incidents = await backend_client.get_incidents()
        
        agent_state = {
            "infrastructure_data": infrastructure,
            "incident_data": incidents,
        }
        result = await self.monitoring_agent.process(agent_state)
        
        state["monitoring_analysis"] = result.get("monitoring_analysis")
        state["infrastructure_list"] = infrastructure
        state["incident_list"] = incidents
        return state
    
    async def _prediction_node(self, state: RecommendationState) -> RecommendationState:
        """Prediction analysis"""
        # Run prediction for overall failure risk
        pred_state = {
            "prediction_type": "failure",
            "horizon_minutes": 360,
            "monitoring_analysis": state.get("monitoring_analysis"),
        }
        result = await self.prediction_agent.process(pred_state)
        state["prediction_analysis"] = result.get("prediction_analysis")
        return state
    
    async def _recovery_node(self, state: RecommendationState) -> RecommendationState:
        """Recovery recommendations"""
        result = await self.recovery_agent.process(state)
        state["recovery_recommendations"] = result.get("recovery_recommendations")
        return state
    
    async def _recommendation_node(self, state: RecommendationState) -> RecommendationState:
        """Final recommendation synthesis"""
        result = await self.recommendation_agent.process(state)
        state["recommendations"] = result.get("recommendations")
        return state
    
    async def generate_recommendations(
        self, 
        infrastructure_ids: List[str] = None,
        incident_ids: List[str] = None,
        force_regenerate: bool = False
    ) -> List[Recommendation]:
        """Generate recommendations"""
        
        # Initialize state
        initial_state: RecommendationState = {
            "infrastructure_list": [],
            "incident_list": [],
            "risk_assessment": {},
            "priority_ranking": [],
            "recommendations": [],
        }
        
        # Run graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Extract recommendations
        recommendations_data = final_state.get("recommendations", [])
        
        # Convert to schema objects
        recommendations = [
            Recommendation(
                id=rec["id"],
                service_id=rec.get("service_id"),
                service_name=rec.get("service_name"),
                title=rec["title"],
                description=rec["description"],
                priority=rec["priority"],
                severity=rec["severity"],
                expected_impact=rec["expected_impact"],
                implementation_steps=rec["implementation_steps"],
                category=rec["category"],
                estimated_effort=rec["estimated_effort"],
                created_at=datetime.fromisoformat(rec["created_at"]) if isinstance(rec["created_at"], str) else rec["created_at"],
                source=rec.get("source", "ai"),
            )
            for rec in recommendations_data
        ]
        
        return recommendations


# Singleton instance
recommendation_service = RecommendationService()
