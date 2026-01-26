"""
Credits API endpoints.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from dependencies import get_current_db_user
from models.credits import CreditLedgerEntry
from models.user import User
from services.credits import create_pending_topup

router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY or "sk_test_placeholder"


class CreditBalanceResponse(BaseModel):
    balance: Decimal
    currency: str


class CreditTopupRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, le=10000)


class CreditTopupResponse(BaseModel):
    checkout_url: str
    session_id: str
    ledger_id: str


class CreditLedgerEntryResponse(BaseModel):
    id: str
    amount: Decimal
    currency: str
    entry_type: str
    status: str
    related_order_id: Optional[str] = None
    posted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CreditLedgerListResponse(BaseModel):
    entries: List[CreditLedgerEntryResponse]
    total: int


def _require_stripe_secret() -> None:
    if not settings.STRIPE_SECRET_KEY and settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=500, detail="Stripe secret key not configured")


@router.get("/balance", response_model=CreditBalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_db_user),
):
    return CreditBalanceResponse(
        balance=Decimal(str(current_user.credit_balance or 0)),
        currency=current_user.credit_currency,
    )


@router.get("/ledger", response_model=CreditLedgerListResponse)
async def list_ledger(
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
):
    result = await db.execute(
        select(CreditLedgerEntry)
        .where(CreditLedgerEntry.user_id == current_user.id)
        .order_by(CreditLedgerEntry.created_at.desc())
        .limit(limit)
    )
    entries = result.scalars().all()
    return CreditLedgerListResponse(
        entries=[CreditLedgerEntryResponse.model_validate(entry) for entry in entries],
        total=len(entries),
    )


@router.post("/topup/session", response_model=CreditTopupResponse)
async def create_topup_session(
    payload: CreditTopupRequest,
    request: Request,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    _require_stripe_secret()

    amount = Decimal(str(payload.amount))
    amount_cents = int(amount * Decimal("100"))

    entry = await create_pending_topup(
        db,
        user_id=current_user.id,
        amount=amount,
        currency=current_user.credit_currency,
        metadata={"credits": str(amount)},
    )

    metadata = {
        "credit_topup": "true",
        "credit_ledger_id": entry.id,
        "user_id": current_user.id,
        "credits": str(amount),
    }

    base_url = settings.APP_URL.rstrip("/") if settings.APP_URL else f"{request.url.scheme}://{request.url.netloc}"

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "MyWork Credits",
                            "description": "Prepaid balance for marketplace purchases",
                        },
                        "unit_amount": amount_cents,
                    },
                    "quantity": 1,
                }
            ],
            metadata=metadata,
            payment_intent_data={"metadata": metadata},
            mode="payment",
            success_url=f"{base_url}/dashboard?credit_topup=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/pricing",
            client_reference_id=entry.id,
            idempotency_key=f"credit_topup_{entry.id}",
        )

        entry.metadata = {
            **(entry.metadata or {}),
            "checkout_session_id": checkout_session.id,
        }
        await db.commit()
        return CreditTopupResponse(
            checkout_url=checkout_session.url,
            session_id=checkout_session.id,
            ledger_id=entry.id,
        )

    except stripe.error.StripeError as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Stripe error: {exc}")
