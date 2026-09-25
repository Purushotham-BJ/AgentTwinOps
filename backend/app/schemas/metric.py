from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class MetricBase(BaseModel):
    service_id: UUID
    cpu_usage: float = Field(default=0.0, ge=0.0, le=100.0)
    memory_usage: float = Field(default=0.0, ge=0.0, le=100.0)
    disk_usage: float = Field(default=0.0, ge=0.0, le=100.0)
    network_usage: float = Field(default=0.0, ge=0.0)
    latency: float = Field(default=0.0, ge=0.0)


class MetricCreate(MetricBase):
    pass


class MetricResponse(MetricBase):
    id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class MetricListResponse(BaseModel):
    items: List[MetricResponse]
    total: int

    model_config = ConfigDict(from_attributes=True)
