"""
Review model for product ratings and feedback.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, generate_uuid


class Review(Base, TimestampMixin):
    """Product review from verified buyers."""

    __tablename__ = "reviews"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    # Relationships
    order_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("orders.id", ondelete="CASCADE"),
        unique=True,  # One review per order
        nullable=False
    )
    buyer_id: Mapped[str] = mapped_column(
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

    # Review content
    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    title: Mapped[Optional[str]] = mapped_column(String(200))
    content: Mapped[Optional[str]] = mapped_column(Text)

    # Engagement
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)

    # Seller response
    seller_response: Mapped[Optional[str]] = mapped_column(Text)
    seller_response_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",  # active, hidden, flagged
        nullable=False
    )

    # Constraints
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='valid_rating'),
    )

    # Relationships
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="review"
    )
    buyer: Mapped["User"] = relationship(
        "User",
        back_populates="reviews"
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="reviews"
    )

    def __repr__(self) -> str:
        return f"<Review {self.id} - {self.rating} stars>"


# Import at bottom to avoid circular imports
from models.order import Order
from models.user import User
from models.product import Product
