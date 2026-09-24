"""Prediction schemas"""
from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime
from .common import RiskLevel, MetricPoint


class PredictionRequest(BaseModel):
    service_id: str
    horizon_minutes: int = Field(default=360, ge=30, le=1440)


class PredictionResult(BaseModel):
    id: str
    service_id: str
    prediction_type: Literal["cpu", "memory", "failure"]
    predicted_value: float
    confidence: float = Field(ge=0.0, le=1.0)
    failure_probability: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    factors: List[str]
    recommended_action: str
    created_at: datetime
    horizon_minutes: int
    data_points: List[MetricPoint]


class PredictionResponse(BaseModel):
    success: bool = True
    data: PredictionResult
    timestamp: datetime = Field(default_factory=datetime.now)
