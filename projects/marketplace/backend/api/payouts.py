"""
Payouts API for seller earnings and payout requests.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from models.user import User
from models.payout import Payout, PAYOUT_STATUSES
from models.order import Order
from models.seller_profile import SellerProfile

router = APIRouter(prefix="/api/payouts", tags=["payouts"])


@router.get("/me")
async def get_seller_payouts(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get seller's payout history."""
    # Build query
    query = select(Payout).where(Payout.seller_id == current_user.id)

    if status:
        query = query.where(Payout.status == status)

    query = query.order_by(Payout.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    payouts = result.scalars().all()

    return {
        "payouts": [
            {
                "id": p.id,
                "amount": float(p.amount),
                "currency": p.currency,
                "order_count": p.order_count,
                "status": p.status,
                "status_label": PAYOUT_STATUSES.get(p.status, p.status),
                "period_start": p.period_start.isoformat(),
                "period_end": p.period_end.isoformat(),
                "initiated_at": p.initiated_at.isoformat() if p.initiated_at else None,
                "completed_at": p.completed_at.isoformat() if p.completed_at else None,
                "failure_reason": p.failure_reason,
                "created_at": p.created_at.isoformat(),
            }
            for p in payouts
        ]
    }


@router.get("/me/balance")
async def get_pending_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get seller's pending balance available for payout."""
    # Check if user is a seller
    seller_profile = await db.execute(
        select(SellerProfile).where(SellerProfile.user_id == current_user.id)
    )
    seller = seller_profile.scalar_one_or_none()

    if not seller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a seller to access payouts"
        )

    # Calculate pending balance from completed orders not yet paid out
    # Orders that are completed but don't have a payout_id
    result = await db.execute(
        select(func.coalesce(func.sum(Order.seller_amount), 0)).where(
            and_(
                Order.seller_id == current_user.id,
                Order.payment_status == "completed",
                Order.payout_id.is_(None)
            )
        )
    )
    pending_balance = result.scalar() or 0

    # Get order count
    result = await db.execute(
        select(func.count(Order.id)).where(
            and_(
                Order.seller_id == current_user.id,
                Order.payment_status == "completed",
                Order.payout_id.is_(None)
            )
        )
    )
    order_count = result.scalar() or 0

    # Get upcoming payout date (usually weekly)
    last_payout = await db.execute(
        select(Payout)
        .where(Payout.seller_id == current_user.id)
        .order_by(Payout.created_at.desc())
        .limit(1)
    )
    last_payout_obj = last_payout.scalar_one_or_none()

    # Calculate next payout date (7 days after last payout or from start)
    if last_payout_obj and last_payout_obj.period_end:
        next_payout_date = last_payout_obj.period_end + timedelta(days=7)
    else:
        # Next Sunday
        today = datetime.now().date()
        days_until_sunday = (6 - today.weekday()) % 7
        next_payout_date = datetime.combine(
            today + timedelta(days=days_until_sunday),
            datetime.min.time()
        )

    return {
        "pending_balance": float(pending_balance),
        "currency": "USD",
        "order_count": order_count,
        "next_payout_date": next_payout_date.isoformat(),
        "payouts_enabled": seller.payouts_enabled,
        "stripe_account_id": seller.stripe_account_id,
    }


@router.post("/me/request")
async def request_payout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request payout of pending balance."""
    # Check if user is a seller
    seller_profile = await db.execute(
        select(SellerProfile).where(SellerProfile.user_id == current_user.id)
    )
    seller = seller_profile.scalar_one_or_none()

    if not seller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a seller to request payouts"
        )

    if not seller.payouts_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payouts are not enabled for your account. Please complete Stripe onboarding."
        )

    # Get unpaid orders
    result = await db.execute(
        select(Order).where(
            and_(
                Order.seller_id == current_user.id,
                Order.payment_status == "completed",
                Order.payout_id.is_(None)
            )
        )
    )
    unpaid_orders = result.scalars().all()

    if not unpaid_orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending balance available for payout"
        )

    # Calculate total amount
    total_amount = sum(order.seller_amount for order in unpaid_orders)

    # Minimum payout amount (e.g., $10)
    if total_amount < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum payout amount is $10.00. You have ${total_amount:.2f} available."
        )

    # Calculate period (last 7 days)
    period_end = datetime.now()
    period_start = period_end - timedelta(days=7)

    # Create payout record
    payout = Payout(
        seller_id=current_user.id,
        amount=total_amount,
        currency="USD",
        order_count=len(unpaid_orders),
        status="pending",
        period_start=period_start,
        period_end=period_end,
    )

    db.add(payout)
    await db.flush()  # Get payout ID

    # Update orders with payout_id
    for order in unpaid_orders:
        order.payout_id = payout.id

    await db.commit()

    return {
        "id": payout.id,
        "amount": float(payout.amount),
        "currency": payout.currency,
        "order_count": payout.order_count,
        "status": payout.status,
        "status_label": PAYOUT_STATUSES[payout.status],
        "message": "Payout requested successfully. Funds will be transferred to your bank account within 2-3 business days."
    }


@router.get("/me/seller-profile")
async def get_seller_payout_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get seller's payout profile status."""
    seller_profile = await db.execute(
        select(SellerProfile).where(SellerProfile.user_id == current_user.id)
    )
    seller = seller_profile.scalar_one_or_none()

    if not seller:
        return {
            "is_seller": False,
            "payouts_enabled": False,
            "stripe_onboarding_complete": False,
            "stripe_account_id": None,
        }

    return {
        "is_seller": True,
        "payouts_enabled": seller.payouts_enabled,
        "stripe_onboarding_complete": seller.stripe_account_id is not None,
        "stripe_account_id": seller.stripe_account_id,
        "charges_enabled": seller.charges_enabled,
    }
