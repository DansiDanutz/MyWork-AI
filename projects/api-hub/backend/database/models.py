"""
API Hub Database Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
from .db import Base


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # Friendly name
    provider = Column(String(50), nullable=False)  # openrouter, deepseek, gemini, openai
    key_value = Column(Text, nullable=False)  # Encrypted/stored key
    key_preview = Column(String(20), nullable=False)  # Last 6 chars for display
    base_url = Column(String(255), nullable=True)  # Provider base URL
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key_id = Column(Integer, nullable=False)
    endpoint = Column(String(255), nullable=True)
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
