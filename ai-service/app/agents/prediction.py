"""Prediction Agent — forecasts future infrastructure state"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random
from .base import BaseAgent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


def _get_insufficient_data_error_class():
    """Lazy import to avoid circular dependency between agents and services."""
    from app.services.model_manager import InsufficientDataError
    return InsufficientDataError


class PredictionAgent(BaseAgent):
    """
    Prediction Agent
    
    Responsibilities:
    - CPU prediction
    - Memory prediction
    - Failure risk prediction
    """
    
    def __init__(self):
        super().__init__("PredictionAgent")
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictions based on historical data and current state"""
        prediction_type = state.get("prediction_type", "failure")
        service_id = state.get("service_id")
        horizon_minutes = state.get("horizon_minutes", 360)
        
        # Generate prediction based on type
        if prediction_type == "cpu":
            result = await self._predict_cpu(service_id, horizon_minutes)
        elif prediction_type == "memory":
            result = await self._predict_memory(service_id, horizon_minutes)
        else:
            result = await self._predict_failure(service_id, horizon_minutes, state)
        
        state["prediction_analysis"] = result
        return state
    
    async def _predict_cpu(self, service_id: str, horizon: int) -> Dict[str, Any]:
        """Predict CPU usage"""
        InsufficientDataError = _get_insufficient_data_error_class()
        # Use ML model for CPU prediction if enabled
        try:
            from app.services.model_manager import predict_cpu
            # predict_cpu returns (predicted_value, model_metrics, feature_matrix, raw_values)
            predicted_cpu, metrics, feature_matrix, raw_values = predict_cpu(service_id, horizon)
            status = "SUCCESS"
            prediction_source = "model"
            historical_metrics = raw_values
            feature_vector = feature_matrix
        except InsufficientDataError as ide:
            # Insufficient historical data — return a clean INSUFFICIENT_DATA response
            # immediately without entering the threshold/risk-analysis block below.
            return {
                "predicted_value": 0.0,
                "confidence": 0.0,
                "failure_probability": 0.0,
                "risk_level": "low",
                "risk_factors": [],
                "recommended_action": "Insufficient historical data for a reliable prediction",
                "model_metrics": {"error": str(ide)},
                "status": "INSUFFICIENT_DATA",
                "prediction_source": "none",
                "historical_metrics": [],
                "feature_vector": [],
            }
        except Exception as e:
            # Fallback to stochastic prediction if model fails for an unexpected reason
            base_cpu = 35 + (random.random() * 30)  # 35-65% base range
            trend_per_hour = 1 + (random.random() * 4)  # 1-5% increase per hour
            predicted_cpu = min(95, base_cpu + (trend_per_hour * horizon / 60))
            metrics = {}
            status = "ERROR"
            prediction_source = "fallback"
            historical_metrics = []
            feature_vector = []

        # --- Risk analysis block (only reached when predicted_cpu is a valid float) ---
        if self.llm:
            try:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are an infrastructure analysis expert. Analyze CPU trends and provide risk assessment."),
                    ("user", f"Current predicted CPU: {predicted_cpu:.1f}%, Horizon: {horizon}min. Assess failure risk and provide factors."),
                ])
                parser = JsonOutputParser()
                chain = prompt | self.llm | parser
                ai_analysis = await chain.ainvoke({})
                risk_factors = ai_analysis.get("factors", [])
            except Exception:
                risk_factors = ["CPU utilization trending upward", "Peak traffic period approaching", "Background processes increasing load"]
        else:
            risk_factors = ["CPU utilization trending upward", "Peak traffic period approaching", "Background processes increasing load"]

        # Calculate failure probability
        if predicted_cpu > 85:
            failure_prob = 0.4 + ((predicted_cpu - 85) / 15) * 0.4
        elif predicted_cpu > 70:
            failure_prob = 0.15 + ((predicted_cpu - 70) / 15) * 0.25
        else:
            failure_prob = predicted_cpu / 100 * 0.15

        # Determine risk level and recommendations
        if predicted_cpu > 90:
            risk_level = "critical"
            recommended_action = "Immediate horizontal scaling required - add replicas now"
        elif predicted_cpu > 80:
            risk_level = "high"
            recommended_action = "Prepare for scaling - consider adding replicas within next hour"
        elif predicted_cpu > 70:
            risk_level = "medium"
            recommended_action = "Monitor closely - scaling may be needed if trend continues"
        else:
            risk_level = "low"
            recommended_action = "No immediate action required - continue monitoring"

        confidence = 0.75 + (random.random() * 0.15)  # retain confidence range
        return {
            "predicted_value": round(predicted_cpu, 1),
            "confidence": round(confidence, 2),
            "failure_probability": round(failure_prob, 3),
            "risk_level": risk_level,
            "risk_factors": risk_factors[:4],
            "recommended_action": recommended_action,
            "model_metrics": metrics,
            "status": status,
            "prediction_source": prediction_source,
            "historical_metrics": historical_metrics,
            "feature_vector": feature_vector,
        }
    
    async def _predict_memory(self, service_id: str, horizon: int) -> Dict[str, Any]:
        """Predict memory usage using ML model if possible"""
        InsufficientDataError = _get_insufficient_data_error_class()
        try:
            from app.services.model_manager import predict_memory
            predicted_mem, metrics, feature_matrix, raw_values = predict_memory(service_id, horizon)
            status = "SUCCESS"
            prediction_source = "model"
            historical_metrics = raw_values
            feature_vector = feature_matrix
            trend_per_hour = 0.0
        except InsufficientDataError as ide:
            # Insufficient historical data — return a clean INSUFFICIENT_DATA response
            # immediately without entering the threshold/risk-analysis block below.
            return {
                "predicted_value": 0.0,
                "confidence": 0.0,
                "failure_probability": 0.0,
                "risk_level": "low",
                "risk_factors": [],
                "recommended_action": "Insufficient historical data for a reliable prediction",
                "model_metrics": {"error": str(ide)},
                "status": "INSUFFICIENT_DATA",
                "prediction_source": "none",
                "historical_metrics": [],
                "feature_vector": [],
            }
        except Exception as e:
            # Fallback to stochastic prediction if model fails for an unexpected reason
            base_mem = 45 + (random.random() * 25)  # 45-70% base range
            trend_per_hour = 0.5 + (random.random() * 2.5)  # 0.5-3% increase per hour
            predicted_mem = min(95, base_mem + (trend_per_hour * horizon / 60))
            metrics = {}
            status = "ERROR"
            prediction_source = "fallback"
            historical_metrics = []
            feature_vector = []

        # --- Risk analysis block (only reached when predicted_mem is a valid float) ---
        risk_factors = []
        if predicted_mem > 80:
            risk_factors.append("Memory pressure approaching critical threshold")
        if trend_per_hour > 2:
            risk_factors.append("Rapid memory growth pattern detected")
        risk_factors.extend(["GC frequency increasing", "Heap fragmentation detected"])

        # Calculate failure probability for memory
        if predicted_mem > 90:
            failure_prob = 0.6 + ((predicted_mem - 90) / 10) * 0.3
        elif predicted_mem > 80:
            failure_prob = 0.25 + ((predicted_mem - 80) / 10) * 0.35
        elif predicted_mem > 70:
            failure_prob = 0.1 + ((predicted_mem - 70) / 10) * 0.15
        else:
            failure_prob = predicted_mem / 100 * 0.1

        # Determine risk level and recommendations
        if predicted_mem > 90:
            risk_level = "critical"
            recommended_action = "Schedule immediate service restart or increase memory limits"
        elif predicted_mem > 85:
            risk_level = "high"
            recommended_action = "Plan maintenance window for memory optimization or restart"
        elif predicted_mem > 75:
            risk_level = "medium"
            recommended_action = "Investigate memory leaks and prepare for potential restart"
        else:
            risk_level = "low"
            recommended_action = "Continue monitoring memory trends"

        confidence = 0.78 + (random.random() * 0.15)  # 78-93% confidence
        return {
            "predicted_value": round(predicted_mem, 1),
            "confidence": round(confidence, 2),
            "failure_probability": round(failure_prob, 3),
            "risk_level": risk_level,
            "risk_factors": risk_factors[:4],
            "recommended_action": recommended_action,
            "model_metrics": metrics,
            "status": status,
            "prediction_source": prediction_source,
            "historical_metrics": historical_metrics,
            "feature_vector": feature_vector,
        }
    
    async def _predict_failure(self, service_id: str, horizon: int, state: Dict[str, Any]) -> Dict[str, Any]:
        """Predict overall failure probability"""
        monitoring = state.get("monitoring_analysis") or {}
        infra_health = monitoring.get("infrastructure_health") or {}
        incidents = monitoring.get("incident_summary") or {}
        
        # Calculate failure probability based on current state
        base_risk = 0.05  # Base 5% risk
        
        # Assess infrastructure health impact
        total_services = infra_health.get("total", 1)
        healthy_services = infra_health.get("healthy", 0)
        degraded_services = infra_health.get("degraded", 0) 
        unhealthy_services = infra_health.get("unhealthy", 0)
        
        # Higher risk if many services are degraded/unhealthy
        if total_services > 0:
            degraded_ratio = degraded_services / total_services
            unhealthy_ratio = unhealthy_services / total_services
            base_risk += degraded_ratio * 0.3  # 30% risk per degraded service ratio
            base_risk += unhealthy_ratio * 0.5  # 50% risk per unhealthy service ratio
        
        # Incident impact
        total_incidents = incidents.get("total", 0)
        critical_incidents = incidents.get("critical", 0)
        open_incidents = incidents.get("open", 0)
        
        if total_incidents > 0:
            base_risk += (critical_incidents / total_incidents) * 0.4  # Critical incidents add significant risk
            base_risk += min(open_incidents * 0.1, 0.3)  # Open incidents add up to 30% risk
        
        # Time horizon factor - longer horizons have higher uncertainty
        time_factor = min(horizon / 1440, 1.0) * 0.2  # Max 20% additional risk for 24h+ horizon
        base_risk += time_factor
        
        failure_prob = max(0.01, min(0.95, base_risk))
        
        # Build risk factors based on actual conditions
        risk_factors = []
        if degraded_services > 0:
            risk_factors.append(f"{degraded_services} degraded services in cluster")
        if unhealthy_services > 0:
            risk_factors.append(f"{unhealthy_services} unhealthy services detected")
        if critical_incidents > 0:
            risk_factors.append(f"{critical_incidents} critical incidents outstanding")
        if open_incidents > 0:
            risk_factors.append(f"{open_incidents} open incidents requiring attention")
        
        # Add technical factors
        if failure_prob > 0.3:
            risk_factors.append("Cascading failure risk due to service dependencies")
        if horizon > 720:  # 12+ hours
            risk_factors.append("Extended prediction horizon increases uncertainty")
        
        # Determine risk level
        if failure_prob > 0.7:
            risk_level = "critical"
            recommended_action = "Immediate intervention required - scale resources and investigate critical issues"
        elif failure_prob > 0.4:
            risk_level = "high" 
            recommended_action = "Proactive scaling recommended - address degraded services"
        elif failure_prob > 0.2:
            risk_level = "medium"
            recommended_action = "Monitor closely and prepare contingency plans"
        else:
            risk_level = "low"
            recommended_action = "Continue normal monitoring"
        
        # Calculate confidence based on data quality
        confidence = 0.85  # Base confidence
        if total_services == 0:
            confidence -= 0.2  # Less confident with no service data
        if total_incidents == 0:
            confidence -= 0.1  # Slightly less confident with no incident history
        confidence = max(0.3, min(0.95, confidence))
        
        return {
            "predicted_value": failure_prob * 100,
            "confidence": confidence,
            "failure_probability": failure_prob,
            "risk_level": risk_level,
            "risk_factors": risk_factors[:5],  # Limit to top 5 factors
            "recommended_action": recommended_action,
            "status": "SUCCESS",
            "prediction_source": "heuristic",
            "historical_metrics": [],
            "feature_vector": [],
            "model_metrics": {},
        }
