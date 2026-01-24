"""
Payout model for seller earnings.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, generate_uuid


class Payout(Base, TimestampMixin):
    """Payout to seller for completed sales."""

    __tablename__ = "payouts"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    # Seller
    seller_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Amount
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Order count
    order_count: Mapped[int] = mapped_column(default=0)

    # Stripe transfer
    stripe_transfer_id: Mapped[Optional[str]] = mapped_column(String(255))
    stripe_payout_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",  # pending, processing, completed, failed
        nullable=False,
        index=True
    )
    failure_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Period covered
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    # Processing timestamps
    initiated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    # Relationships
    seller: Mapped["User"] = relationship("User")
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="payout"
    )

    def __repr__(self) -> str:
        return f"<Payout {self.id} - ${self.amount}>"

    @property
    def is_completed(self) -> bool:
        """Check if payout is completed."""
        return self.status == "completed"


# Payout statuses
PAYOUT_STATUSES = {
    "pending": "Waiting to be processed",
    "processing": "Transfer initiated",
    "completed": "Funds transferred",
    "failed": "Transfer failed",
}


# Import at bottom
from models.user import User
from models.order import Order
