"""Recommendation schemas"""
from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime
from .common import IncidentSeverity


class RecommendationPriority(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationCategory(str):
    SCALING = "scaling"
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    RELIABILITY = "reliability"
    COST = "cost"


class Recommendation(BaseModel):
    id: str
    service_id: str | None = None
    service_name: str | None = None
    title: str
    description: str
    priority: Literal["low", "medium", "high", "critical"]
    severity: Literal["low", "medium", "high", "critical"]
    expected_impact: str
    implementation_steps: List[str]
    category: Literal["scaling", "optimization", "security", "reliability", "cost"]
    estimated_effort: Literal["low", "medium", "high"]
    created_at: datetime
    source: Literal["ai", "rule", "manual"] = "ai"


class RecommendationListResponse(BaseModel):
    success: bool = True
    data: List[Recommendation]
    timestamp: datetime = Field(default_factory=datetime.now)


class RecommendationGenerateRequest(BaseModel):
    infrastructure_ids: List[str] = Field(default_factory=list)
    incident_ids: List[str] = Field(default_factory=list)
    force_regenerate: bool = False
