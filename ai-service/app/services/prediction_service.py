"""Prediction service with LangGraph orchestration"""
import logging
from typing import Dict, Any
from datetime import datetime
from uuid import uuid4
from langgraph.graph import StateGraph, END
from app.orchestration.state import PredictionState
from app.agents import MonitoringAgent, PredictionAgent
from app.services.backend_client import backend_client
from app.schemas.prediction import PredictionResult
from app.schemas.common import MetricPoint

logger = logging.getLogger(__name__)


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
        auth_token = state.get("auth_token")
        infrastructure = await backend_client.get_infrastructure(auth_token=auth_token)
        incidents = await backend_client.get_incidents(auth_token=auth_token)

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
        horizon_minutes: int = 360,
        auth_token: str | None = None,
    ) -> PredictionResult:
        """Generate prediction for service and, on success, persist predicted_state to the twin."""

        # Initialize state
        initial_state: PredictionState = {
            "service_id": service_id,
            "auth_token": auth_token,
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
                value=analysis.get("predicted_value", 0) * (0.8 + i * 0.05),
            )
            for i in range(min(12, horizon_minutes // 30))
        ]

        # Build PredictionResult
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
            status=analysis.get("status", "SUCCESS"),
            historical_metrics=analysis.get("historical_metrics", []),
            feature_vector=analysis.get("feature_vector", []),
            model_metrics=analysis.get("model_metrics", {}),
            prediction_source=analysis.get(
                "prediction_source",
                "heuristic" if prediction_type == "failure" else "model",
            ),
        )

        # -----------------------------------------------------------------
        # Twin predicted_state synchronization
        # Only sync when we have a real ML prediction (status == SUCCESS).
        # Do NOT sync for INSUFFICIENT_DATA or ERROR — those carry no
        # meaningful forecast to persist.
        # -----------------------------------------------------------------
        if result.status == "SUCCESS":
            predicted_state = self._build_predicted_state(result, prediction_type, horizon_minutes)
            try:
                if auth_token:
                    await backend_client.update_twin_predicted_state(
                        service_id, predicted_state, auth_token=auth_token
                    )
                else:
                    await backend_client.update_twin_predicted_state(service_id, predicted_state)
                logger.info(
                    "Twin predicted_state updated for service=%s type=%s",
                    service_id,
                    prediction_type,
                )
            except Exception as sync_exc:
                # Prediction succeeded; twin sync failed.
                # Log honestly and carry on — do NOT corrupt the prediction result.
                logger.error(
                    "Twin predicted_state sync FAILED for service=%s: %s",
                    service_id,
                    sync_exc,
                )
                # Surface the sync failure in model_metrics so the caller can
                # inspect it without changing the top-level status field.
                result.model_metrics = dict(result.model_metrics)
                result.model_metrics["twin_sync_error"] = str(sync_exc)

        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_predicted_state(
        result: PredictionResult,
        prediction_type: str,
        horizon_minutes: int,
    ) -> Dict[str, Any]:
        """Build the predicted_state dict to persist on the twin.

        Uses only values present in PredictionResult — no invented fields.
        """
        state: Dict[str, Any] = {
            "prediction_type": prediction_type,
            "predicted_value": result.predicted_value,
            "failure_probability": result.failure_probability,
            "confidence": result.confidence,
            "risk_level": result.risk_level,
            "recommended_action": result.recommended_action,
            "prediction_timestamp": result.created_at.isoformat(),
            "horizon_minutes": horizon_minutes,
            "prediction_source": result.prediction_source,
        }
        # Include model quality metrics if the ML model produced them
        if result.model_metrics:
            state["model_metrics"] = result.model_metrics
        return state


# Singleton instance
prediction_service = PredictionService()
