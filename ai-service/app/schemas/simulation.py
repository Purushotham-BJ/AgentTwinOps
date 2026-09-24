"""Simulation schemas"""
from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Any
from datetime import datetime
from .common import MetricPoint


class SimulationScenario(str):
    CPU_SPIKE = "cpu_spike"
    TRAFFIC_SURGE = "traffic_surge"
    DATABASE_FAILURE = "database_failure"
    POD_EVICTION = "pod_eviction"


class SimulationRequest(BaseModel):
    scenario: Literal["cpu_spike", "traffic_surge", "database_failure", "pod_eviction"]
    service_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class SimulationImpact(BaseModel):
    cpu_delta: float
    memory_delta: float
    latency_delta: float
    failure_probability: float = Field(ge=0.0, le=1.0)


class SimulationResult(BaseModel):
    id: str
    scenario: str
    service_id: str
    status: Literal["running", "completed", "failed"]
    predicted_impact: SimulationImpact
    timeline: List[MetricPoint]
    recommendations: List[str]
    created_at: datetime
    completed_at: datetime | None = None


class SimulationResponse(BaseModel):
    success: bool = True
    data: SimulationResult
    timestamp: datetime = Field(default_factory=datetime.now)
