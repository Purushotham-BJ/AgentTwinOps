"""Schemas for the authenticated multi-agent operations workflow."""
from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class OrchestrationRequest(BaseModel):
    service_id: str = Field(min_length=1)
    include_prediction: bool = True
    include_simulation: bool = True
    include_recovery: bool = True
    horizon_minutes: int = Field(default=360, ge=30, le=1440)


class AgentExecution(BaseModel):
    agent: str
    status: str
    error: str | None = None


class OrchestrationResponse(BaseModel):
    success: bool = True
    service_id: str
    status: str
    operational_status: str
    health_score: float
    failure_probability: float
    agents: List[AgentExecution]
    monitoring: Dict[str, Any]
    predictions: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    simulations: List[Dict[str, Any]]
    recovery_actions: List[Dict[str, Any]]
    errors: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)
