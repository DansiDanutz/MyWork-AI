"""
Escrow release helpers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.order import Order


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def release_due_escrow(db: AsyncSession) -> int:
    """Mark escrow as released for due orders. Returns number of orders updated."""
    now = _now()
    result = await db.execute(
        select(Order)
        .where(Order.payment_status == "completed")
        .where(Order.status == "completed")
        .where(Order.escrow_release_at.is_not(None))
        .where(Order.escrow_release_at <= now)
        .where(Order.escrow_released.is_(False))
    )
    orders: Iterable[Order] = result.scalars().all()
    updated = 0
    for order in orders:
        order.escrow_released = True
        updated += 1
    return updated
