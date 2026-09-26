from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TwinState(BaseModel):
    cpu: float = 0.0
    memory: float = 0.0
    status: str = "unknown"


class TwinBase(BaseModel):
    service_id: UUID
    current_state: Dict[str, Any] = {}
    predicted_state: Dict[str, Any] = {}
    health_score: float = 100.0
    failure_probability: float = 0.0


class TwinCreate(TwinBase):
    pass


class TwinResponse(TwinBase):
    id: UUID
    last_sync: datetime
    # Sprint 5 extensions
    operational_status: str
    state_version: int
    trends: Dict[str, Any]
    anomalies: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)


class TwinHistoryResponse(BaseModel):
    id: UUID
    twin_id: UUID
    state: Dict[str, Any]
    health_score: float
    state_version: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
