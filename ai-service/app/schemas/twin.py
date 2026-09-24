"""Digital Twin schemas"""
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime
from .common import InfrastructureStatus


class TwinSyncStatus(str):
    SYNCED = "synced"
    SYNCING = "syncing"
    OUT_OF_SYNC = "out_of_sync"
    ERROR = "error"


class TwinState(BaseModel):
    cpu_usage: float = Field(ge=0.0, le=100.0)
    memory_usage: float = Field(ge=0.0, le=100.0)
    latency_ms: float = Field(ge=0.0)
    error_rate: float = Field(ge=0.0, le=100.0)
    request_rate: float = Field(ge=0.0)
    status: str


class TwinObject(BaseModel):
    id: str
    name: str
    service_id: str
    service_type: str
    current_state: TwinState
    predicted_state: TwinState
    health_score: float = Field(ge=0.0, le=100.0)
    sync_status: Literal["synced", "syncing", "out_of_sync", "error"]
    last_synced: datetime


class TwinListResponse(BaseModel):
    success: bool = True
    data: list[TwinObject]
    timestamp: datetime = Field(default_factory=datetime.now)


class TwinResponse(BaseModel):
    success: bool = True
    data: TwinObject
    timestamp: datetime = Field(default_factory=datetime.now)
