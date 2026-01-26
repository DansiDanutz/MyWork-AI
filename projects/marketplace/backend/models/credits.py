"""
Credits ledger for marketplace stored value.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, generate_uuid


CREDIT_ENTRY_TYPES = [
    "topup",
    "purchase",
    "sale",
    "fee",
    "refund",
    "escrow_hold",
    "escrow_release",
    "adjustment",
]


class CreditLedgerEntry(Base, TimestampMixin):
    """Immutable ledger entry for credit movement."""

    __tablename__ = "credit_ledger"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    entry_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="posted",  # posted, pending, reversed
        nullable=False,
        index=True,
    )

    related_order_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("orders.id"),
        index=True,
    )

    related_submission_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("project_submissions.id"),
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship("User")
    order: Mapped[Optional["Order"]] = relationship("Order")
    submission: Mapped[Optional["ProjectSubmission"]] = relationship("ProjectSubmission")

    def __repr__(self) -> str:
        return f"<CreditLedgerEntry {self.id} {self.amount}>"


# Import at bottom to avoid circular imports
from models.user import User
from models.order import Order
from models.submission import ProjectSubmission
