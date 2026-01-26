"""
Credit ledger helpers for marketplace stored-value balance.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Dict, Any, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.credits import CreditLedgerEntry


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _as_decimal(value: object) -> Decimal:
    return Decimal(str(value or 0))


async def create_pending_topup(
    db: AsyncSession,
    user_id: str,
    amount: Decimal,
    currency: str = "USD",
    metadata: Optional[Dict[str, Any]] = None,
) -> CreditLedgerEntry:
    entry = CreditLedgerEntry(
        user_id=user_id,
        amount=amount,
        currency=currency,
        entry_type="topup",
        status="pending",
        metadata=metadata,
    )
    db.add(entry)
    await db.flush()
    return entry


async def finalize_topup(
    db: AsyncSession,
    ledger_id: str,
) -> Optional[CreditLedgerEntry]:
    entry = await db.get(CreditLedgerEntry, ledger_id)
    if not entry or entry.status == "posted":
        return entry

    user = await db.scalar(
        select(User).where(User.id == entry.user_id).with_for_update()
    )
    if not user:
        raise ValueError("User not found for credit top-up")

    current = _as_decimal(user.credit_balance)
    user.credit_balance = current + _as_decimal(entry.amount)

    entry.status = "posted"
    entry.posted_at = _now()
    return entry


async def mark_topup_failed(db: AsyncSession, ledger_id: str) -> Optional[CreditLedgerEntry]:
    entry = await db.get(CreditLedgerEntry, ledger_id)
    if not entry or entry.status in ("posted", "reversed"):
        return entry
    entry.status = "reversed"
    entry.posted_at = _now()
    return entry


async def apply_credit_purchase(
    db: AsyncSession,
    *,
    buyer_id: str,
    seller_id: str,
    amount: Decimal,
    platform_fee: Decimal,
    order_id: str,
    currency: str = "USD",
    metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[CreditLedgerEntry, CreditLedgerEntry]:
    """Apply a credit-based purchase and return ledger entries (buyer, seller)."""
    amount = _as_decimal(amount)
    platform_fee = _as_decimal(platform_fee)
    seller_amount = amount - platform_fee

    if amount <= 0:
        raise ValueError("Purchase amount must be positive")

    result = await db.execute(
        select(User)
        .where(User.id.in_([buyer_id, seller_id]))
        .order_by(User.id)
        .with_for_update()
    )
    users = {user.id: user for user in result.scalars()}
    buyer = users.get(buyer_id)
    seller = users.get(seller_id)

    if not buyer or not seller:
        raise ValueError("Buyer or seller not found")

    buyer_balance = _as_decimal(buyer.credit_balance)
    if buyer_balance < amount:
        raise ValueError("Insufficient credit balance")

    buyer.credit_balance = buyer_balance - amount
    seller.credit_balance = _as_decimal(seller.credit_balance) + seller_amount

    now = _now()
    buyer_entry = CreditLedgerEntry(
        user_id=buyer_id,
        amount=-amount,
        currency=currency,
        entry_type="purchase",
        status="posted",
        related_order_id=order_id,
        description="Purchase",
        metadata=metadata,
        posted_at=now,
    )
    seller_entry = CreditLedgerEntry(
        user_id=seller_id,
        amount=seller_amount,
        currency=currency,
        entry_type="sale",
        status="posted",
        related_order_id=order_id,
        description="Sale",
        metadata=metadata,
        posted_at=now,
    )
    db.add_all([buyer_entry, seller_entry])
    return buyer_entry, seller_entry
