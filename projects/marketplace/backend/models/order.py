"""
Order model for marketplace purchases.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, generate_uuid


def generate_order_number() -> str:
    """Generate a unique order number."""
    import random
    from datetime import datetime
    year = datetime.utcnow().year
    random_part = random.randint(10000, 99999)
    return f"MW-{year}-{random_part}"


class Order(Base, TimestampMixin):
    """Order/purchase in the marketplace."""

    __tablename__ = "orders"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    # Order number (human-readable)
    order_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        default=generate_order_number,
        index=True
    )

    # Parties
    buyer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    seller_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    # Pricing at time of purchase
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    license_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # Fee breakdown
    platform_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    stripe_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    seller_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Stripe payment
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(String(255))
    stripe_charge_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Payment status
    payment_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",  # pending, processing, completed, failed, refunded
        nullable=False,
        index=True
    )

    # Fulfillment
    download_url: Mapped[Optional[str]] = mapped_column(Text)
    download_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    download_count: Mapped[int] = mapped_column(Integer, default=0)

    # Order status
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",  # pending, completed, refunded, disputed
        nullable=False,
        index=True
    )

    # Escrow
    escrow_release_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    escrow_released: Mapped[bool] = mapped_column(default=False)

    # Refund info
    refund_reason: Mapped[Optional[str]] = mapped_column(Text)
    refunded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    refund_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))

    # Payout tracking
    payout_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("payouts.id")
    )

    # Relationships
    buyer: Mapped["User"] = relationship(
        "User",
        back_populates="purchases",
        foreign_keys=[buyer_id]
    )
    seller: Mapped["User"] = relationship(
        "User",
        foreign_keys=[seller_id]
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="orders"
    )
    review: Mapped[Optional["Review"]] = relationship(
        "Review",
        back_populates="order",
        uselist=False
    )
    payout: Mapped[Optional["Payout"]] = relationship(
        "Payout",
        back_populates="orders"
    )

    def __repr__(self) -> str:
        return f"<Order {self.order_number}>"

    @property
    def is_completed(self) -> bool:
        """Check if order is completed."""
        return self.status == "completed" and self.payment_status == "completed"

    @property
    def can_be_refunded(self) -> bool:
        """Check if order can be refunded (within 14 days)."""
        if self.status != "completed":
            return False
        if self.refunded_at:
            return False
        days_since_purchase = (datetime.utcnow() - self.created_at).days
        return days_since_purchase <= 14

    @property
    def can_be_reviewed(self) -> bool:
        """Check if buyer can leave a review."""
        return self.is_completed and self.review is None


# Order statuses
ORDER_STATUSES = {
    "pending": "Waiting for payment",
    "completed": "Payment received, product delivered",
    "refunded": "Order refunded",
    "disputed": "Under dispute",
}

PAYMENT_STATUSES = {
    "pending": "Awaiting payment",
    "processing": "Payment processing",
    "completed": "Payment successful",
    "failed": "Payment failed",
    "refunded": "Payment refunded",
}


# Import at bottom to avoid circular imports
from models.user import User
from models.product import Product
from models.review import Review
from models.payout import Payout
