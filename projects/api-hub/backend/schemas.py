"""
API Hub Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    provider: str = Field(..., min_length=1, max_length=50)
    key_value: str = Field(..., min_length=5)
    base_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class APIKeyResponse(BaseModel):
    id: int
    name: str
    provider: str
    key_preview: str  # Masked — only last 6 chars
    base_url: Optional[str]
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime
    total_requests: int
    total_tokens: int
    total_cost: float

    class Config:
        from_attributes = True


class APIKeyUsage(BaseModel):
    key_id: int
    name: str
    provider: str
    total_requests: int
    total_tokens: int
    total_cost: float
    recent_logs: list = []


class UsageLogResponse(BaseModel):
    id: int
    api_key_id: int
    endpoint: Optional[str]
    tokens_used: int
    cost: float
    status_code: Optional[int]
    response_time_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    total_keys: int
    active_keys: int
    total_requests: int
    total_tokens: int
    total_cost: float
    providers: dict
    top_keys: list
