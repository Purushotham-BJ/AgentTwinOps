"""Common schemas"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricPoint(BaseModel):
    timestamp: datetime
    value: float


class InfrastructureStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InfrastructureData(BaseModel):
    """Infrastructure data from backend API"""
    id: str
    service_name: str
    service_type: str
    status: str
    host: str
    created_at: datetime
    updated_at: datetime


class IncidentData(BaseModel):
    """Incident data from backend API"""
    id: str
    service_id: str
    severity: str
    incident_type: str
    resolution_status: str
    timestamp: datetime
