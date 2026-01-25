"""
Configuration management for MyWork Marketplace.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "MyWork Marketplace"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # URLs
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"

    # Database (SQLite for dev, PostgreSQL for prod)
    DATABASE_URL: str = "sqlite+aiosqlite:///./marketplace.db"

    # Redis
    REDIS_URL: Optional[str] = None

    # Authentication (Clerk)
    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_WEBHOOK_SECRET: str = ""
    CLERK_FRONTEND_API: str = "clerk.mywork.ai"  # Your Clerk frontend API domain

    # Payments (Stripe)
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_CONNECT_CLIENT_ID: str = ""

    # Platform fees
    PLATFORM_FEE_PERCENT: float = 10.0  # 10% platform fee
    ESCROW_DAYS: int = 7  # 7-day escrow period

    # AI (Anthropic)
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"

    # Vector Database (Pinecone)
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX: str = "mywork-brain"

    # Storage (Cloudflare R2/S3)
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET: str = "marketplace-files"
    R2_ENDPOINT: str = ""
    R2_PUBLIC_URL: str = ""  # Optional public base URL for images

    # Email (Resend)
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@mywork.ai"

    # Subscription Tiers
    PRO_PRICE_ID: str = ""  # Stripe Price ID for Pro tier
    TEAM_PRICE_ID: str = ""  # Stripe Price ID for Team tier
    ENTERPRISE_PRICE_ID: str = ""  # Stripe Price ID for Enterprise

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience instance
settings = get_settings()
