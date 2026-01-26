"""
User and SellerProfile models.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, generate_uuid


class User(Base, TimestampMixin):
    """User model - represents all users (buyers and sellers)."""

    __tablename__ = "users"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    # Clerk integration
    clerk_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    # Basic info
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    display_name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)

    # Role and status
    role: Mapped[str] = mapped_column(
        String(20),
        default="buyer",  # buyer, seller, admin
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Stripe integration
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Subscription
    subscription_tier: Mapped[str] = mapped_column(
        String(20),
        default="free",  # free, pro, team, enterprise
        nullable=False
    )
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    # Credits (stored value)
    credit_balance: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0.00,
        nullable=False,
    )
    credit_currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )

    # Relationships
    seller_profile: Mapped[Optional["SellerProfile"]] = relationship(
        "SellerProfile",
        back_populates="user",
        uselist=False
    )
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="seller",
        foreign_keys="Product.seller_id"
    )
    purchases: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="buyer",
        foreign_keys="Order.buyer_id"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review",
        back_populates="buyer"
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    @property
    def is_seller(self) -> bool:
        """Check if user is a seller."""
        return self.role in ("seller", "admin")

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == "admin"

    @property
    def is_pro(self) -> bool:
        """Check if user has Pro subscription."""
        if self.subscription_tier in ("pro", "team", "enterprise"):
            if self.subscription_expires_at:
                return self.subscription_expires_at > datetime.utcnow()
        return False


class SellerProfile(Base, TimestampMixin):
    """Extended profile for sellers."""

    __tablename__ = "seller_profiles"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    # Foreign key to user
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    # Profile info
    bio: Mapped[Optional[str]] = mapped_column(Text)
    website: Mapped[Optional[str]] = mapped_column(String(255))
    github_username: Mapped[Optional[str]] = mapped_column(String(50))
    twitter_handle: Mapped[Optional[str]] = mapped_column(String(50))

    # Stripe Connect
    stripe_connect_id: Mapped[Optional[str]] = mapped_column(String(255))
    stripe_connect_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",  # pending, active, restricted, disabled
        nullable=False
    )
    payouts_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Stats (denormalized for performance)
    total_sales: Mapped[int] = mapped_column(default=0)
    total_revenue: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0.00
    )
    average_rating: Mapped[float] = mapped_column(
        Numeric(3, 2),
        default=0.00
    )
    review_count: Mapped[int] = mapped_column(default=0)

    # Verification
    verification_level: Mapped[str] = mapped_column(
        String(20),
        default="basic",  # basic, verified, premium
        nullable=False
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    # Settings
    payout_schedule: Mapped[str] = mapped_column(
        String(20),
        default="weekly",  # weekly, monthly
        nullable=False
    )
    minimum_payout: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=50.00
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="seller_profile")

    def __repr__(self) -> str:
        return f"<SellerProfile {self.user_id}>"

    @property
    def can_receive_payouts(self) -> bool:
        """Check if seller can receive payouts."""
        return (
            self.stripe_connect_status == "active" and
            self.payouts_enabled
        )


# Import at bottom to avoid circular imports
from models.product import Product
from models.order import Order
from models.review import Review
