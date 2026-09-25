"""Prediction schemas"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Literal
from datetime import datetime
from .common import RiskLevel, MetricPoint


class PredictionRequest(BaseModel):
    service_id: str
    horizon_minutes: int = Field(default=360, ge=30, le=1440)


class PredictionResult(BaseModel):
    # Suppress the "model_" namespace warning from Pydantic — the field name
    # model_metrics is intentional and not a conflicting config option.
    model_config = ConfigDict(protected_namespaces=())

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
    # Sprint 6 fields
    status: Literal["SUCCESS", "INSUFFICIENT_DATA", "ERROR"] = "SUCCESS"
    historical_metrics: List[float] = []   # raw metric values used for prediction
    feature_vector: List[List[float]] = [] # feature matrix used in model
    model_metrics: dict = {}               # e.g., mae, rmse, r2
    prediction_source: Literal["model", "heuristic", "fallback", "none"] = "model"


class PredictionResponse(BaseModel):
    success: bool = True
    data: PredictionResult
    timestamp: datetime = Field(default_factory=datetime.now)
