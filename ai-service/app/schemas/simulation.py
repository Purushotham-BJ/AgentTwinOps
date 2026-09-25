"""Schemas for deterministic Digital Twin what-if simulations."""
from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field, field_validator

from .common import MetricPoint


ScenarioName = Literal[
    "cpu_spike",
    "traffic_surge",
    "database_failure",
    "pod_eviction",
    "custom",
]


class SimulationRequest(BaseModel):
    scenario: ScenarioName = "custom"
    service_id: str = Field(min_length=1)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    horizon_minutes: int = Field(default=60, ge=1, le=1440)

    @field_validator("parameters")
    @classmethod
    def validate_parameters(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        numeric_fields = {"cpu_usage", "memory_usage", "latency_ms"}
        for key in numeric_fields.intersection(value):
            number = value[key]
            if isinstance(number, bool) or not isinstance(number, (int, float)):
                raise ValueError(f"{key} must be numeric")
            if key != "latency_ms" and not 0 <= number <= 100:
                raise ValueError(f"{key} must be between 0 and 100")
            if key == "latency_ms" and number < 0:
                raise ValueError("latency_ms must be non-negative")
        if "status" in value and value["status"] not in {
            "active", "healthy", "degraded", "unhealthy", "inactive"
        }:
            raise ValueError("status is not a supported infrastructure status")
        return value


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
    baseline_state: Dict[str, Any]
    scenario_changes: Dict[str, Any]
    simulated_state: Dict[str, Any]
    simulated_health_score: float = Field(ge=0.0, le=100.0)
    simulated_failure_probability: float = Field(ge=0.0, le=1.0)
    simulated_operational_status: str
    impact_summary: List[str]
    predicted_impact: SimulationImpact
    timeline: List[MetricPoint]
    recommendations: List[str]
    created_at: datetime
    completed_at: datetime | None = None


class SimulationResponse(BaseModel):
    success: bool = True
    data: SimulationResult
    timestamp: datetime = Field(default_factory=datetime.now)
