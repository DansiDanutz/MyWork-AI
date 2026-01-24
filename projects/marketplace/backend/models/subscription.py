"""
Subscription model for Pro/Team/Enterprise tiers.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, generate_uuid


class Subscription(Base, TimestampMixin):
    """User subscription for premium features."""

    __tablename__ = "subscriptions"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    # User relationship
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Tier
    tier: Mapped[str] = mapped_column(
        String(20),
        nullable=False  # pro, team, enterprise
    )

    # Stripe subscription
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255))
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(255))
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",  # active, canceled, past_due, incomplete
        nullable=False,
        index=True
    )

    # Billing period
    current_period_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    current_period_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    # Cancellation
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    canceled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    # Trial
    trial_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    trial_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    # Relationships
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<Subscription {self.user_id} - {self.tier}>"

    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        if self.status not in ("active", "trialing"):
            return False
        if self.current_period_end:
            return self.current_period_end > datetime.utcnow()
        return True

    @property
    def is_trialing(self) -> bool:
        """Check if subscription is in trial period."""
        if self.trial_end:
            return self.trial_end > datetime.utcnow()
        return False


# Subscription tiers configuration
SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Community",
        "price": 0,
        "features": [
            "Framework access",
            "Basic Brain queries (10/day)",
            "Community support",
        ],
        "limits": {
            "brain_queries_per_day": 10,
            "can_sell": False,
        },
    },
    "pro": {
        "name": "Pro",
        "price": 49,
        "features": [
            "Everything in Free",
            "Sell on marketplace",
            "Unlimited Brain queries",
            "Priority support",
            "Analytics dashboard",
            "Verified seller badge",
        ],
        "limits": {
            "brain_queries_per_day": -1,  # unlimited
            "can_sell": True,
        },
    },
    "team": {
        "name": "Team",
        "price": 149,
        "features": [
            "Everything in Pro",
            "5 team seats",
            "Shared Brain workspace",
            "Team analytics",
            "Custom branding",
        ],
        "limits": {
            "brain_queries_per_day": -1,
            "can_sell": True,
            "team_seats": 5,
        },
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 499,
        "features": [
            "Everything in Team",
            "Unlimited seats",
            "White-label option",
            "Dedicated support",
            "SLA guarantee",
            "Custom integrations",
        ],
        "limits": {
            "brain_queries_per_day": -1,
            "can_sell": True,
            "team_seats": -1,  # unlimited
        },
    },
}


# Import at bottom
from models.user import User
