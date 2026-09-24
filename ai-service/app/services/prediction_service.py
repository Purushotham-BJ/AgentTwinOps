"""Prediction service with LangGraph orchestration"""
from typing import Dict, Any
from datetime import datetime
from uuid import uuid4
from langgraph.graph import StateGraph, END
from app.orchestration.state import PredictionState
from app.agents import MonitoringAgent, PredictionAgent
from app.services.backend_client import backend_client
from app.schemas.prediction import PredictionResult
from app.schemas.common import MetricPoint


class PredictionService:
    """Service for generating infrastructure predictions"""
    
    def __init__(self):
        self.monitoring_agent = MonitoringAgent()
        self.prediction_agent = PredictionAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph for prediction workflow"""
        workflow = StateGraph(PredictionState)
        
        # Add nodes
        workflow.add_node("monitoring", self._monitoring_node)
        workflow.add_node("prediction", self._prediction_node)
        
        # Define edges
        workflow.set_entry_point("monitoring")
        workflow.add_edge("monitoring", "prediction")
        workflow.add_edge("prediction", END)
        
        return workflow.compile()
    
    async def _monitoring_node(self, state: PredictionState) -> PredictionState:
        """Monitoring analysis node"""
        # Fetch infrastructure data
        infrastructure = await backend_client.get_infrastructure()
        incidents = await backend_client.get_incidents()
        
        # Run monitoring agent
        agent_state = {
            "infrastructure_data": infrastructure,
            "incident_data": incidents,
        }
        result = await self.monitoring_agent.process(agent_state)
        
        state["monitoring_analysis"] = result.get("monitoring_analysis")
        return state
    
    async def _prediction_node(self, state: PredictionState) -> PredictionState:
        """Prediction generation node"""
        result = await self.prediction_agent.process(state)
        state["prediction_analysis"] = result.get("prediction_analysis")
        return state
    
    async def predict(
        self, 
        service_id: str, 
        prediction_type: str = "failure",
        horizon_minutes: int = 360
    ) -> PredictionResult:
        """Generate prediction for service"""
        
        # Initialize state
        initial_state: PredictionState = {
            "service_id": service_id,
            "prediction_type": prediction_type,
            "horizon_minutes": horizon_minutes,
            "infrastructure_data": [],
            "incident_data": [],
            "historical_metrics": [],
            "monitoring_analysis": None,
            "prediction_analysis": None,
            "feature_vector": [],
            "model_prediction": 0.0,
            "confidence": 0.0,
            "risk_factors": [],
            "predicted_value": 0.0,
            "failure_probability": 0.0,
            "risk_level": "low",
            "recommended_action": "",
            "forecast_timeline": [],
        }
        
        # Run graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Extract results
        analysis = final_state.get("prediction_analysis", {})
        
        # Generate forecast timeline
        now = datetime.now()
        from datetime import timedelta
        timeline = [
            MetricPoint(
                timestamp=now + timedelta(minutes=i * 30),
                value=analysis.get("predicted_value", 0) * (0.8 + i * 0.05)
            )
            for i in range(min(12, horizon_minutes // 30))
        ]
        
        # Build result
        result = PredictionResult(
            id=str(uuid4()),
            service_id=service_id,
            prediction_type=prediction_type,
            predicted_value=analysis.get("predicted_value", 0.0),
            confidence=analysis.get("confidence", 0.75),
            failure_probability=analysis.get("failure_probability", 0.0),
            risk_level=analysis.get("risk_level", "low"),
            factors=analysis.get("risk_factors", []),
            recommended_action=analysis.get("recommended_action", "No action required"),
            created_at=datetime.now(),
            horizon_minutes=horizon_minutes,
            data_points=timeline,
        )
        
        return result


# Singleton instance
prediction_service = PredictionService()
