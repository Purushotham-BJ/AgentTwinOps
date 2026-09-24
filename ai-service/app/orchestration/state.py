"""LangGraph state definitions for multi-agent orchestration"""
from typing import TypedDict, List, Dict, Any, Literal
from datetime import datetime


class AgentState(TypedDict, total=False):
    """Shared state across all agents in the graph"""
    # Input
    request_type: Literal["prediction", "simulation", "recommendation", "twin"]
    service_id: str
    scenario: str | None
    parameters: Dict[str, Any]
    
    # Context from backend
    infrastructure_data: List[Dict[str, Any]]
    incident_data: List[Dict[str, Any]]
    metrics_data: List[Dict[str, Any]]
    
    # Agent processing
    monitoring_analysis: Dict[str, Any] | None
    prediction_analysis: Dict[str, Any] | None
    simulation_result: Dict[str, Any] | None
    recovery_recommendations: List[Dict[str, Any]]
    cost_recommendations: List[Dict[str, Any]]
    
    # Output
    final_result: Dict[str, Any]
    error: str | None
    timestamp: datetime


class PredictionState(TypedDict, total=False):
    """State for prediction workflow"""
    service_id: str
    prediction_type: Literal["cpu", "memory", "failure"]
    horizon_minutes: int
    
    # Backend data
    infrastructure_data: List[Dict[str, Any]]
    incident_data: List[Dict[str, Any]]
    
    # Historical data
    historical_metrics: List[Dict[str, Any]]
    
    # Analysis
    monitoring_analysis: Dict[str, Any] | None
    prediction_analysis: Dict[str, Any] | None
    feature_vector: List[float]
    model_prediction: float
    confidence: float
    risk_factors: List[str]
    
    # Output
    predicted_value: float
    failure_probability: float
    risk_level: str
    recommended_action: str
    forecast_timeline: List[Dict[str, Any]]


class SimulationState(TypedDict, total=False):
    """State for simulation workflow"""
    scenario: str
    service_id: str
    parameters: Dict[str, Any]
    
    # Current state
    baseline_state: Dict[str, Any]
    
    # Simulation
    simulated_state: Dict[str, Any]
    impact_analysis: Dict[str, Any]
    timeline: List[Dict[str, Any]]
    
    # Recommendations
    mitigation_steps: List[str]


class RecommendationState(TypedDict, total=False):
    """State for recommendation generation"""
    infrastructure_list: List[Dict[str, Any]]
    incident_list: List[Dict[str, Any]]
    
    # Analysis
    monitoring_analysis: Dict[str, Any] | None
    prediction_analysis: Dict[str, Any] | None
    recovery_recommendations: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    priority_ranking: List[Dict[str, Any]]
    
    # Output
    recommendations: List[Dict[str, Any]]
